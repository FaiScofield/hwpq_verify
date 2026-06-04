#include "dci_request_io.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "cJSON.h"

/* ------------------------------------------------------------------ */
/* Internal JSON helpers                                              */
/* ------------------------------------------------------------------ */

static bool dci_json_get_int(cJSON *parent, const char *key, int *out_value,
                             std::string *error_msg) {
    cJSON *node = cJSON_GetObjectItemCaseSensitive(parent, key);
    if (!cJSON_IsNumber(node)) {
        if (error_msg)
            *error_msg = std::string("missing or invalid int field: ") + key;
        return false;
    }
    *out_value = node->valueint;
    return true;
}

static bool dci_json_get_number_as_float(cJSON *parent, const char *key,
                                         float *out_value,
                                         std::string *error_msg) {
    cJSON *node = cJSON_GetObjectItemCaseSensitive(parent, key);
    if (!cJSON_IsNumber(node)) {
        if (error_msg)
            *error_msg =
                std::string("missing or invalid float field: ") + key;
        return false;
    }
    *out_value = static_cast<float>(node->valuedouble);
    return true;
}

static bool dci_json_get_string(cJSON *parent, const char *key,
                                std::string *out_value,
                                std::string *error_msg) {
    cJSON *node = cJSON_GetObjectItemCaseSensitive(parent, key);
    if (!cJSON_IsString(node)) {
        if (error_msg)
            *error_msg =
                std::string("missing or invalid string field: ") + key;
        return false;
    }
    *out_value = node->valuestring;
    return true;
}

static bool dci_parse_override_cfg(cJSON *override_obj,
                                   dci_audit_override_t *cfg,
                                   std::string *error_msg) {
    return dci_json_get_int(override_obj, "enable_cf_he_ratio_override",
                            &cfg->enable_cf_he_ratio_override, error_msg) &&
           dci_json_get_int(override_obj, "cf_he_ratio", &cfg->cf_he_ratio,
                            error_msg) &&
           dci_json_get_int(override_obj, "enable_bs_set_point_override",
                            &cfg->enable_bs_set_point_override, error_msg) &&
           dci_json_get_int(override_obj, "bs_set_point", &cfg->bs_set_point,
                            error_msg) &&
           dci_json_get_int(override_obj, "enable_ws_set_point_override",
                            &cfg->enable_ws_set_point_override, error_msg) &&
           dci_json_get_int(override_obj, "ws_set_point", &cfg->ws_set_point,
                            error_msg) &&
           dci_json_get_int(override_obj, "enable_clahe_local_ratio_override",
                            &cfg->enable_clahe_local_ratio_override,
                            error_msg) &&
           dci_json_get_int(override_obj, "clahe_local_ratio",
                            &cfg->clahe_local_ratio, error_msg) &&
           dci_json_get_int(override_obj, "enable_clahe_clip_value_override",
                            &cfg->enable_clahe_clip_value_override,
                            error_msg) &&
           dci_json_get_number_as_float(override_obj, "clahe_clip_value",
                                        &cfg->clahe_clip_value, error_msg);
}

static bool dci_parse_audit_section(cJSON *audit_obj,
                                    dci_audit_param_t *audit,
                                    std::string *error_msg) {
    std::string tmp;

    if (!dci_json_get_int(audit_obj, "enable", &audit->enable, error_msg))
        return false;
    if (!dci_json_get_int(audit_obj, "static_only", &audit->static_only,
                          error_msg))
        return false;
    if (!dci_json_get_int(audit_obj, "node_mask", (int *)&audit->node_mask, error_msg))
        return false;
    if (!dci_json_get_int(audit_obj, "export_mask", (int *)&audit->export_mask,
                          error_msg))
        return false;

    if (dci_json_get_string(audit_obj, "tag", &tmp, nullptr)) {
        snprintf(audit->tag, sizeof(audit->tag), "%s", tmp.c_str());
    }

    if (dci_json_get_string(audit_obj, "working_dir", &tmp, nullptr)) {
        snprintf(audit->working_dir, sizeof(audit->working_dir), "%s",
                 tmp.c_str());
    }

    if (!dci_json_get_int(audit_obj, "save_snapshot", &audit->save_snapshot,
                          error_msg))
        return false;

    if (dci_json_get_string(audit_obj, "snapshot_dir", &tmp, nullptr)) {
        snprintf(audit->snapshot_dir, sizeof(audit->snapshot_dir), "%s",
                 tmp.c_str());
    }

    /* Parse override_cfg subsection if present */
    cJSON *override_obj =
        cJSON_GetObjectItemCaseSensitive(audit_obj, "override_cfg");
    if (override_obj) {
        if (!dci_parse_override_cfg(override_obj, &audit->override_cfg,
                                    error_msg))
            return false;
    }

    return true;
}

/* ------------------------------------------------------------------ */
/* Public API                                                         */
/* ------------------------------------------------------------------ */

bool dci_load_runner_request(const char *request_path,
                             dci_runner_request_t *request,
                             std::string *error_msg) {
    if (!request_path || !request) {
        if (error_msg) *error_msg = "null argument";
        return false;
    }

    /* Read the entire file */
    FILE *fp = fopen(request_path, "rb");
    if (!fp) {
        if (error_msg)
            *error_msg =
                std::string("cannot open request file: ") + request_path;
        return false;
    }
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    char *buf = static_cast<char *>(malloc(size + 1));
    if (!buf) {
        fclose(fp);
        if (error_msg) *error_msg = "memory allocation failed";
        return false;
    }
    fread(buf, 1, size, fp);
    buf[size] = '\0';
    fclose(fp);

    /* Parse JSON */
    cJSON *root = cJSON_Parse(buf);
    free(buf);
    if (!root) {
        if (error_msg)
            *error_msg = std::string("JSON parse error: ") +
                         cJSON_GetErrorPtr();
        return false;
    }

    bool ok = true;

    ok = ok && dci_json_get_int(root, "platform", &request->platform, error_msg);
    ok = ok && dci_json_get_string(root, "input_file", &request->input_file, error_msg);
    ok = ok && dci_json_get_string(root, "output_file", &request->output_file, error_msg);
    ok = ok && dci_json_get_int(root, "width", &request->width, error_msg);
    ok = ok && dci_json_get_int(root, "height", &request->height, error_msg);
    ok = ok && dci_json_get_int(root, "pixel_format", &request->pixel_format, error_msg);
    ok = ok && dci_json_get_int(root, "input_format", &request->input_format, error_msg);
    ok = ok && dci_json_get_int(root, "input_colorspace", &request->input_colorspace, error_msg);
    ok = ok && dci_json_get_int(root, "output_format", &request->output_format, error_msg);
    ok = ok && dci_json_get_int(root, "output_colorspace", &request->output_colorspace, error_msg);

    /* Optional fields with defaults */
    std::string tmp;
    if (dci_json_get_string(root, "config_path", &tmp, nullptr))
        request->config_path = tmp;
    if (dci_json_get_string(root, "reg_path", &tmp, nullptr))
        request->reg_path = tmp;

    dci_json_get_int(root, "is_src_fullrange", &request->is_src_fullrange, nullptr);
    dci_json_get_int(root, "frame_idx", &request->frame_idx, nullptr);
    dci_json_get_int(root, "frame_num", &request->frame_num, nullptr);
    dci_json_get_int(root, "debug_dump_mask", &request->debug_dump_mask, nullptr);

    if (dci_json_get_string(root, "debug_path", &tmp, nullptr))
        request->debug_path = tmp;

    /* Parse audit section */
    cJSON *audit_obj = cJSON_GetObjectItemCaseSensitive(root, "audit");
    if (audit_obj) {
        ok = ok && dci_parse_audit_section(audit_obj, &request->audit, error_msg);
    }

    cJSON_Delete(root);
    return ok;
}

bool dci_write_runner_result(const char *result_path,
                             const dci_runner_result_t &result,
                             std::string *error_msg) {
    if (!result_path) {
        if (error_msg) *error_msg = "null result_path";
        return false;
    }

    cJSON *root = cJSON_CreateObject();
    cJSON_AddNumberToObject(root, "exit_code", result.exit_code);
    cJSON_AddStringToObject(root, "status", result.status.c_str());
    cJSON_AddStringToObject(root, "message", result.message.c_str());
    cJSON_AddStringToObject(root, "working_dir", result.working_dir.c_str());

    char *json_str = cJSON_Print(root);
    cJSON_Delete(root);
    if (!json_str) {
        if (error_msg) *error_msg = "JSON serialisation failed";
        return false;
    }

    FILE *fp = fopen(result_path, "w");
    if (!fp) {
        free(json_str);
        if (error_msg)
            *error_msg =
                std::string("cannot write result file: ") + result_path;
        return false;
    }
    fputs(json_str, fp);
    fclose(fp);
    free(json_str);
    return true;
}
