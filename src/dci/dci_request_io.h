#ifndef _DCI_REQUEST_IO_H_
#define _DCI_REQUEST_IO_H_

#include "dci_api.h"
#include <string>

/**
 * @brief  Request-side native structs that mirror the Layer 1 JSON contract.
 *         These hold the parsed JSON fields before they are translated into
 *         the dci_init_param_t / dci_proc_param_t structs consumed by the
 *         DCI verification library.
 */
struct dci_runner_request_t {
    int platform = 0;
    std::string input_file;
    std::string output_file;
    int width = 0;
    int height = 0;
    int pixel_format = 0;
    int input_format = 0;
    int input_colorspace = 0;
    int output_format = 0;
    int output_colorspace = 0;
    std::string config_path;
    std::string reg_path;
    int is_src_fullrange = 1;
    int frame_idx = 0;
    int frame_num = 1;
    int debug_dump_mask = 0;
    std::string debug_path;
    dci_audit_param_t audit{};
};

/**
 * @brief  Result struct written to runner_result.json after each execution.
 */
struct dci_runner_result_t {
    int exit_code = 0;
    std::string status;
    std::string message;
    std::string working_dir;
};

/**
 * @brief  Load a runner request from a JSON file.
 * @param  request_path  Path to the request JSON file.
 * @param  request       [out] Parsed request struct.
 * @param  error_msg     [out] Error description on failure (optional).
 * @return true on success, false on parse/validation error.
 */
bool dci_load_runner_request(const char *request_path,
                             dci_runner_request_t *request,
                             std::string *error_msg);

/**
 * @brief  Write runner result to a JSON file.
 * @param  result_path  Path to write the result JSON.
 * @param  result       Result data to serialise.
 * @param  error_msg    [out] Error description on failure (optional).
 * @return true on success, false on file write error.
 */
bool dci_write_runner_result(const char *result_path,
                             const dci_runner_result_t &result,
                             std::string *error_msg);

#endif /* _DCI_REQUEST_IO_H_ */