"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : verify_bcsh_native.py
Author      : vance.wu@rock-chips.com
Date        : 2026-10-19
Description : 调用 rk_swpq_exe 与本工程 hsv_adjust.py，对 BCSH 结果做数值比对。
              用法示例:
                python script/bcsh/verify_bcsh_native.py --quick
                python script/bcsh/verify_bcsh_native.py --exe <rk_swpq_exe> --model both
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from script.bcsh.native_compare import (  # noqa: E402
    BcshNativeConfig,
    NativeBcshError,
    NativeBcshRunner,
    build_cases,
    compare_rgb,
    find_default_exe,
    load_image_chart,
    make_test_chart,
    proc_mode_value,
    python_reference,
    same_target_antipode_mask,
    write_report_csv,
)

_DEFAULT_OUT_DIR = _REPO_ROOT / "output" / "bcsh_native"
_REPORT_FIELDS = [
    "index",
    "name",
    "model",
    "proc_mode",
    "color_space",
    "brightness",
    "contrast",
    "saturation",
    "hue",
    "hue_goal",
    "max_abs",
    "mean_abs",
    "p99_abs",
    "count_gt1",
    "count_gt2",
    "total",
    "masked_px",
    "threshold",
    "alpha_ok",
    "passed",
    "elapsed_s",
    "error",
]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="BCSH: hsv_adjust.py 与 rk_swpq_exe 的自动数值比对",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--exe", help="rk_swpq_exe 路径；默认自动查找或读 RKPQ_EXE")
    parser.add_argument("--out-dir", default=str(_DEFAULT_OUT_DIR),
                        help="报告与失败用例图片的输出目录")
    parser.add_argument("--model", choices=("rgb", "hsv", "both"), default="both",
                        help="验证的 BCSH 颜色模型")
    parser.add_argument("--proc-mode", choices=("auto", "gpu", "cpu", "cpu_gpu"),
                        default="gpu", help="C++ 处理单元（cpu 需要无 OpenCL 构建）")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--quick", action="store_true", help="只跑少量代表用例")
    group.add_argument("--full", action="store_true", help="跑更密集的参数组合")
    parser.add_argument("--size", type=int, default=256,
                        help="测试图边长（>=128 且为 16 的倍数）")
    parser.add_argument("--seed", type=int, default=0, help="随机测试图/随机参数种子")
    parser.add_argument("--image", help="改用真实图片（自动缩放到 --size）")
    parser.add_argument("--threshold-rgb", type=int, default=2,
                        help="RGB 模型允许的最大绝对误差（LSB）")
    parser.add_argument("--threshold-hsv", type=int, default=3,
                        help="HSV 模型允许的最大绝对误差（LSB）")
    parser.add_argument("--timeout", type=float, default=180.0,
                        help="单次 rk_swpq_exe 调用的超时时间（秒）")
    parser.add_argument("--save-all", action="store_true",
                        help="保存所有用例的输入/参考/输出/diff 图")
    parser.add_argument("--no-artifacts", action="store_true",
                        help="不保存任何图片")
    parser.add_argument("--keep-temp", action="store_true",
                        help="保留每次调用的临时目录（调试用）")
    parser.add_argument("--fail-fast", action="store_true",
                        help="遇到第一条超差/失败用例即退出")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="输出调试日志（exe 路径/参数/临时目录/输出统计）")
    parser.add_argument("--list-cases", action="store_true",
                        help="只打印用例列表，不执行")
    return parser


def _save_artifacts(
    case_dir: Path,
    chart: np.ndarray,
    reference: np.ndarray,
    native: np.ndarray,
) -> None:
    """保存输入、参考、C++ 输出和放大后的 diff 图。"""
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise ImportError("保存图片需要 Pillow") from exc

    case_dir.mkdir(parents=True, exist_ok=True)
    Image.fromarray(chart).save(case_dir / "input.png")
    Image.fromarray(reference).save(case_dir / "ref.png")
    Image.fromarray(native).save(case_dir / "native.png")
    diff = np.abs(native.astype(np.int16) - reference.astype(np.int16))
    diff_img = np.clip(diff * 8, 0, 255).astype(np.uint8)
    Image.fromarray(diff_img).save(case_dir / "diff_x8.png")


def _print_case_line(
    index: int,
    total: int,
    name: str,
    config: BcshNativeConfig,
    metrics,
    threshold: int,
    alpha_ok: bool,
    elapsed: float,
    error: str | None,
) -> None:
    prefix = f"[{index:02d}/{total:02d}] {name:24s}"
    if error:
        print(f"{prefix} ERROR: {error}")
        return
    verdict = "PASS" if metrics.max_abs <= threshold and alpha_ok else "FAIL"
    alpha_text = "" if alpha_ok else " alpha=CHANGED"
    masked_text = "" if not metrics.masked else f" masked_px={metrics.masked}"
    print(
        f"{prefix} {config.label():48s} "
        f"max={metrics.max_abs} mean={metrics.mean_abs:.4f} "
        f"p99={metrics.p99_abs:.1f} >1={metrics.count_gt1} "
        f">2={metrics.count_gt2}{masked_text} {elapsed:5.2f}s {verdict}{alpha_text}"
    )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    exe = Path(args.exe) if args.exe else find_default_exe()
    if args.list_cases:
        cases = build_cases(
            args.model, quick=args.quick, full=args.full, seed=args.seed
        )
        for case in cases:
            print(f"{case.name:28s} {case.config.label()}")
        print(f"共 {len(cases)} 条用例")
        return 0

    if exe is None:
        print(
            "找不到 rk_swpq_exe。请用 --exe 指定，或设置环境变量 RKPQ_EXE，"
            "或设置 RKYUVALGOS_ROOT 指向 RkYuvAlgos_git 仓库根目录。",
            file=sys.stderr,
        )
        return 2
    if not exe.is_file():
        print(f"rk_swpq_exe 不存在: {exe}", file=sys.stderr)
        return 2

    try:
        proc_mode = proc_mode_value(args.proc_mode)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    try:
        chart = (
            load_image_chart(args.image, args.size)
            if args.image
            else make_test_chart(args.size, args.seed)
        )
    except (ValueError, OSError) as exc:
        print(f"生成测试图失败: {exc}", file=sys.stderr)
        return 2

    cases = build_cases(args.model, quick=args.quick, full=args.full, seed=args.seed)
    if not cases:
        print("没有可执行的用例", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"可执行程序: {exe}")
    print(f"处理模式  : {args.proc_mode} ({proc_mode})")
    print(f"测试图    : {args.image or f'synthetic {args.size}x{args.size}'}")
    print(f"用例数量  : {len(cases)}")
    print("-" * 110)

    runner = NativeBcshRunner(
        exe, timeout=args.timeout, keep_temp=args.keep_temp
    )

    rows: list[dict] = []
    passed_num = 0
    failed_num = 0
    start_all = time.perf_counter()

    for index, case in enumerate(cases, 1):
        config = replace(case.config, proc_mode=proc_mode)
        threshold = (
            args.threshold_rgb if config.model == "rgb" else args.threshold_hsv
        )
        start = time.perf_counter()
        error: str | None = None
        metrics = None
        alpha_ok = True
        native = None
        reference = None

        try:
            native_rgba = runner.run(chart, config)
            native = native_rgba[..., :3]
            alpha_ok = bool(np.all(native_rgba[..., 3] == 255))
            reference = python_reference(chart, config)
            mask = same_target_antipode_mask(chart, config)
            metrics = compare_rgb(reference, native, mask=mask)
            if int(reference.max()) > 0 and int(native.max()) == 0:
                raise NativeBcshError(
                    "rk_swpq_exe 输出全黑（期望结果非全黑）：exe 可能与 "
                    "D:/RkDefaultDumpData/pq_bcsh_*.bin 的 OpenCL kernel 缓存不匹配。\n"
                    f"当前 exe: {exe}\n"
                    "请改用与当前源码同时构建的 rk_swpq_exe，或删除该缓存文件后重试。"
                )
        except (NativeBcshError, RuntimeError, ValueError, OSError) as exc:
            error = str(exc)
            if "Unknown PQ module 13" in error or "Invalid target module id: 13" in error:
                error += "\n提示: 该 rk_swpq_exe 早于 BCSH 模块，需要重新编译。"

        elapsed = time.perf_counter() - start
        _print_case_line(
            index, len(cases), case.name, config, metrics, threshold,
            alpha_ok, elapsed, error,
        )

        ok = bool(metrics is not None and metrics.max_abs <= threshold and alpha_ok)
        if ok:
            passed_num += 1
        else:
            failed_num += 1
            if not args.no_artifacts and metrics is not None:
                try:
                    _save_artifacts(
                        out_dir / case.name, chart, reference, native
                    )
                    print(f"         diff 图: {out_dir / case.name / 'diff_x8.png'}")
                except (OSError, ImportError) as exc:
                    print(f"         保存图片失败: {exc}")
            if (
                config.proc_mode == 2
                and metrics is not None
                and metrics.max_abs == 255
                and not alpha_ok
            ):
                print(
                    "         提示: 当前 OpenCL 构建的 rk_swpq_exe 纯 CPU 模式可能"
                    "被内部 OCL buffer 回读覆盖；请改用 --proc-mode gpu，"
                    "或使用 -DENABLE_RKOCL_SUPPORT=OFF 的纯 CPU 构建。"
                )

        rows.append(
            {
                "index": index,
                "name": case.name,
                "model": config.model,
                "proc_mode": proc_mode,
                "color_space": config.color_space,
                "brightness": config.brightness,
                "contrast": config.contrast,
                "saturation": config.saturation,
                "hue": config.hue,
                "hue_goal": config.hue_goal,
                "max_abs": "" if metrics is None else metrics.max_abs,
                "mean_abs": "" if metrics is None else f"{metrics.mean_abs:.6f}",
                "p99_abs": "" if metrics is None else f"{metrics.p99_abs:.3f}",
                "count_gt1": "" if metrics is None else metrics.count_gt1,
                "count_gt2": "" if metrics is None else metrics.count_gt2,
                "total": "" if metrics is None else metrics.total,
                "masked_px": "" if metrics is None else metrics.masked,
                "threshold": threshold,
                "alpha_ok": int(alpha_ok),
                "passed": int(ok),
                "elapsed_s": f"{elapsed:.3f}",
                "error": error or "",
            }
        )

        if args.save_all and not args.no_artifacts and metrics is not None:
            try:
                _save_artifacts(out_dir / case.name, chart, reference, native)
            except (OSError, ImportError) as exc:
                print(f"         保存图片失败: {exc}")

        if args.fail_fast and not ok:
            print("已按 --fail-fast 停止。")
            break

    total_elapsed = time.perf_counter() - start_all
    report_path = out_dir / "report.csv"
    write_report_csv(report_path, rows, _REPORT_FIELDS)

    print("-" * 110)
    print(
        f"结果: {passed_num}/{len(rows)} 通过, {failed_num} 失败, "
        f"总耗时 {total_elapsed:.1f}s"
    )
    print(f"报告: {report_path}")
    return 0 if failed_num == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
