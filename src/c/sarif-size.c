// sarif-size.c
// Fast JSON structure size profiler using yyjson
// Example: ./sarif-size-c file.sarif [max_depth]

#include "yyjson.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int max_depth = 4;               // adjustable recursion depth limit

// Compute approximate size contribution of a node
static size_t sizeof_value(yyjson_val *v) {
    switch (yyjson_get_type(v)) {
        case YYJSON_TYPE_OBJ: {
            size_t idx, max;
            yyjson_val *k, *val;
            size_t total = 0;
            yyjson_obj_foreach(v, idx, max, k, val) {
                total += yyjson_get_len(k) + sizeof_value(val);
            }
            return total;
        }
        case YYJSON_TYPE_ARR: {
            size_t idx, max;
            yyjson_val *itm;
            size_t total = 0;
            yyjson_arr_foreach(v, idx, max, itm) {
                total += sizeof_value(itm);
            }
            return total;
        }
        case YYJSON_TYPE_STR:
            return yyjson_get_len(v);
        default:
            return 8; // number, bool, null
    }
}

// Recursive traversal with depth limit
static void walk_limited(yyjson_val *v, const char *path, int depth) {
    if (depth > max_depth) return;

    size_t s = sizeof_value(v);
    printf("%10zu  %s\n", s, path);

    if (yyjson_is_obj(v) && depth < max_depth) {
        size_t idx, max;
        yyjson_val *k, *val;
        yyjson_obj_foreach(v, idx, max, k, val) {
            char subpath[512];
            snprintf(subpath, sizeof(subpath), "%s.%.*s",
                     path, (int)yyjson_get_len(k), yyjson_get_str(k));
            walk_limited(val, subpath, depth + 1);
        }
    } else if (yyjson_is_arr(v) && depth < max_depth) {
        size_t idx, max;
        yyjson_val *itm;
        yyjson_arr_foreach(v, idx, max, itm) {
            char subpath[256];
            snprintf(subpath, sizeof(subpath), "%s[%zu]", path, idx);
            walk_limited(itm, subpath, depth + 1);
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s file.json [depth]\n", argv[0]);
        return 1;
    }
    if (argc > 2) {
        int d = atoi(argv[2]);
        if (d > 0) max_depth = d;
    }

    // Replace the chunked loop with this simple version:

    FILE *fp = fopen(argv[1], "rb");
    if (!fp) {
      perror("fopen");
      return 1;
    }

    fseek(fp, 0, SEEK_END);
    size_t n = ftell(fp);
    rewind(fp);

    void *buf = malloc(n);
    if (!buf) {
      fprintf(stderr, "Out of memory (%zu bytes)\n", n);
      fclose(fp);
      return 1;
    }
    fread(buf, 1, n, fp);
    fclose(fp);

    yyjson_read_flag fl = YYJSON_READ_STOP_WHEN_DONE;
    yyjson_read_err err;
    yyjson_doc *doc = yyjson_read_opts(buf, n, fl, NULL, &err);
    if (!doc) {
      fprintf(stderr, "Parse error: %s (pos=%zu)\n", err.msg, err.pos);
      free(buf);
      return 1;
    }

    walk_limited(yyjson_doc_get_root(doc), "root", 0);
    yyjson_doc_free(doc);
    free(buf);

    return 0;
}
