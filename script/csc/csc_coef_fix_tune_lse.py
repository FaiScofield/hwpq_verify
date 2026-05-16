"""
ITU-R BT.601-7 Annex 2: Optimization of Integer Coefficients for Luminance and Colour-difference Equations

This script implements the Least Square Error (LSE) optimization method described in Annex 2.
Given the coefficient bit-length m (e.g., 8, 9, 10, ...) and the input RGB signal range [L, H],
it computes optimized integer coefficients for Y, Cb, Cr such that the squared error sum
between integer-based and ideal floating-point-based matrixing is minimized.
"""

import argparse
import math

def sum_x_range(L, H, power=1):
    """
    Returns sum_{x=L}^{H} x^power
    """
    if power == 1:
        # sum = (H+H^2)/2 - ((L-1)+(L-1)^2)/2? Actually formula: H(H+1)/2 - (L-1)L/2
        return H*(H+1)//2 - (L-1)*L//2
    elif power == 2:
        # sum x^2 = H(H+1)(2H+1)/6 - (L-1)L(2L-1)/6
        return H*(H+1)*(2*H+1)//6 - (L-1)*L*(2*L-1)//6
    else:
        raise ValueError("power must be 1 or 2")

def compute_N1_N2(L, H):
    """
    Compute constants N1 and N2 as defined in Annex 2, page 20.
    N1 = (H-L+1)^2 * sum_{x=L}^{H} x^2
    N2 = (H-L+1) * (sum_{x=L}^{H} x)^2
    """
    K = H - L + 1                     # number of integer levels
    sum_x = sum_x_range(L, H, 1)
    sum_x2 = sum_x_range(L, H, 2)
    N1 = (K ** 2) * sum_x2
    N2 = K * (sum_x ** 2)
    return N1, N2

def squared_error_sum(delta1, delta2, delta3, N1, N2, m):
    """
    Compute the squared error sum epsilon' as in equation (14).
    delta = integer_coefficient - real_coefficient (before rounding).
    epsilon = (1/2^m) * [ N1*(d1^2+d2^2+d3^2) + 2*N2*(d1*d2 + d2*d3 + d3*d1) ]
    """
    d1, d2, d3 = delta1, delta2, delta3
    term1 = N1 * (d1*d1 + d2*d2 + d3*d3)
    term2 = 2 * N2 * (d1*d2 + d2*d3 + d3*d1)
    return (term1 + term2) / (2**m)

def optimize_coefficients(r1, r2, r3, N1, N2, m):
    """
    Optimize integer coefficients k1,k2,k3 for given real coefficients r1,r2,r3.
    Returns best integer coefficients (k1, k2, k3) and the resulting error.
    """
    # Initial integer coefficients: nearest integer
    k1_init = int(round(r1))
    k2_init = int(round(r2))
    k3_init = int(round(r3))

    best_k = (k1_init, k2_init, k3_init)
    best_error = squared_error_sum(k1_init - r1, k2_init - r2, k3_init - r3, N1, N2, m)

    # Enumerate all combinations of -1,0,+1 for each coefficient
    for d1 in (-1, 0, 1):
        for d2 in (-1, 0, 1):
            for d3 in (-1, 0, 1):
                k1 = k1_init + d1
                k2 = k2_init + d2
                k3 = k3_init + d3
                delta1 = k1 - r1
                delta2 = k2 - r2
                delta3 = k3 - r3
                err = squared_error_sum(delta1, delta2, delta3, N1, N2, m)
                if err < best_error - 1e-12:  # tolerance
                    best_error = err
                    best_k = (k1, k2, k3)

    return best_k, best_error

def get_real_coefficients_y(m):
    """Real coefficients for Y (luminance) multiplied by 2^m."""
    r1 = 0.299 * (2**m)
    r2 = 0.587 * (2**m)
    r3 = 0.114 * (2**m)
    return r1, r2, r3

def get_real_coefficients_cb(m):
    """
    Real coefficients for Cb (colour difference blue) multiplied by 2^m.
    Based on equations given in Annex 2:
    r_CB1' = -0.299/1.772 * 224/219 * 2^m
    r_CB2' = -0.587/1.772 * 224/219 * 2^m
    r_CB3' =  0.886/1.772 * 224/219 * 2^m
    """
    factor = (224.0 / 219.0) / 1.772
    r1 = -0.299 * factor * (2**m)
    r2 = -0.587 * factor * (2**m)
    r3 =  0.886 * factor * (2**m)
    return r1, r2, r3

def get_real_coefficients_cr(m):
    """
    Real coefficients for Cr (colour difference red) multiplied by 2^m.
    r_CR1' =  0.701/1.402 * 224/219 * 2^m
    r_CR2' = -0.587/1.402 * 224/219 * 2^m
    r_CR3' = -0.114/1.402 * 224/219 * 2^m
    """
    factor = (224.0 / 219.0) / 1.402
    r1 =  0.701 * factor * (2**m)
    r2 = -0.587 * factor * (2**m)
    r3 = -0.114 * factor * (2**m)
    return r1, r2, r3

def print_optimization_result(name, m, L, H, real_coeffs, best_coeffs, error):
    print(f"\n{name} coefficients (m={m}):")
    print(f"  Real (x2^{m}):     {real_coeffs[0]:.6f}, {real_coeffs[1]:.6f}, {real_coeffs[2]:.6f}")
    print(f"  Optimized integer: {best_coeffs[0]:4d}, {best_coeffs[1]:4d}, {best_coeffs[2]:4d}")
    print(f"  Squared error sum: {error:.4f}")

def main():
    parser = argparse.ArgumentParser(description="ITU-R BT.601-7 Annex 2 Coefficient Optimization")
    parser.add_argument('-L', type=int, default=16, help='Input signal range: lower bound (default: 16)')
    parser.add_argument('-H', type=int, default=235, help='Input signal range: upper bound (default: 235)')
    parser.add_argument('-m', type=int, default=8, choices=range(8, 17),
                        help='Coefficient bit-length, 8 to 16 (default: 8)')
    args = parser.parse_args()

    L = args.L
    H = args.H
    m = args.m

    print("ITU-R BT.601-7 Annex 2 Coefficient Optimization")
    print(f"Signal range L={L}, H={H} (active video)")
    print(f"Coefficient bit-length m={m}")

    # Compute constants N1, N2 (same for Y, Cb, Cr)
    N1, N2 = compute_N1_N2(L, H)
    print(f"\nN1 = {N1}, N2 = {N2}")

    # Optimize Y
    r_y = get_real_coefficients_y(m)
    best_y, err_y = optimize_coefficients(r_y[0], r_y[1], r_y[2], N1, N2, m)
    print_optimization_result("Y", m, L, H, r_y, best_y, err_y)

    # Optimize Cb
    r_cb = get_real_coefficients_cb(m)
    best_cb, err_cb = optimize_coefficients(r_cb[0], r_cb[1], r_cb[2], N1, N2, m)
    print_optimization_result("Cb", m, L, H, r_cb, best_cb, err_cb)

    # Optimize Cr
    r_cr = get_real_coefficients_cr(m)
    best_cr, err_cr = optimize_coefficients(r_cr[0], r_cr[1], r_cr[2], N1, N2, m)
    print_optimization_result("Cr", m, L, H, r_cr, best_cr, err_cr)

    # Check against Table 2 of the Recommendation (m = 8 .. 16)
    table2_m8_to_m16 = {
        8:  {"Y": (77, 150, 29), "Cb": (-44, -87, 131), "Cr": (131, -110, -21)},
        9:  {"Y": (153, 301, 58), "Cb": (-88, -174, 262), "Cr": (262, -219, -43)},
        10: {"Y": (306, 601, 117), "Cb": (-177, -347, 524), "Cr": (524, -439, -85)},
        11: {"Y": (612, 1202, 234), "Cb": (-353, -694, 1047), "Cr": (1047, -877, -170)},
        12: {"Y": (1225, 2404, 467), "Cb": (-707, -1388, 2095), "Cr": (2095, -1754, -341)},
        13: {"Y": (2449, 4809, 934), "Cb": (-1414, -2776, 4190), "Cr": (4189, -3508, -681)},
        14: {"Y": (4899, 9617, 1868), "Cb": (-2828, -5551, 8379), "Cr": (8379, -7016, -1363)},
        15: {"Y": (9798, 19235, 3735), "Cb": (-5655, -11103, 16758), "Cr": (16758, -14033, -2725)},
        16: {"Y": (19595, 38470, 7471), "Cb": (-11311, -22205, 33516), "Cr": (33516, -28066, -5450)},
    }
    print(f"\nComparison with Table 2 (m={m}):")
    if m in table2_m8_to_m16:
        expected = table2_m8_to_m16[m]
        print(f"  Table2 Y : {expected['Y']} -> {'OK' if best_y == expected['Y'] else 'Mismatch'}")
        print(f"  Table2 Cb: {expected['Cb']} -> {'OK' if best_cb == expected['Cb'] else 'Mismatch'}")
        print(f"  Table2 Cr: {expected['Cr']} -> {'OK' if best_cr == expected['Cr'] else 'Mismatch'}")
    else:
        print(f"  No Table 2 reference data for m={m}")

if __name__ == "__main__":
    main()