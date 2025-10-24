// yyjson-du.c
#include "yyjson.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Entry {
    char *path;
    size_t size;
} Entry;

static Entry *entries = NULL;
static size_t entry_cap = 0, entry_len = 0;

static void add_entry(const char *path, size_t size) {
    if (entry_len == entry_cap) {
        entry_cap = entry_cap ? entry_cap * 2 : 1024;
        entries = realloc(entries, entry_cap * sizeof(Entry));
        if (!entries) {
            fprintf(stderr, "Out of memory\n");
            exit(1);
        }
    }
    entries[entry_len].path = strdup(path);
    entries[entry_len].size = size;
    entry_len++;
}

static size_t sizeof_value(yyjson_val *v);

static size_t sizeof_array(yyjson_val *arr) {
    size_t idx, max;
    yyjson_val *itm;
    size_t total = 0;
    yyjson_arr_foreach(arr, idx, max, itm) {
        total += sizeof_value(itm);
    }
    return total;
}

static size_t sizeof_obj(yyjson_val *obj) {
    size_t idx, max;
    yyjson_val *k, *v;
    size_t total = 0;
    yyjson_obj_foreach(obj, idx, max, k, v) {
        total += yyjson_get_len(k) + sizeof_value(v);
    }
    return total;
}

static size_t sizeof_value(yyjson_val *v) {
    switch (yyjson_get_type(v)) {
        case YYJSON_TYPE_OBJ: return sizeof_obj(v);
        case YYJSON_TYPE_ARR: return sizeof_array(v);
        case YYJSON_TYPE_STR: return yyjson_get_len(v);
        default: return 8; // numbers, bools, null
    }
}

static void walk(yyjson_val *v, const char *path) {
    size_t s = sizeof_value(v);
    add_entry(path, s);

    if (yyjson_is_obj(v)) {
        size_t idx, max;
        yyjson_val *k, *val;
        yyjson_obj_foreach(v, idx, max, k, val) {
            char subpath[4096];
            snprintf(subpath, sizeof(subpath), "%s.%.*s",
                     path, (int)yyjson_get_len(k), yyjson_get_str(k));
            walk(val, subpath);
        }
    } else if (yyjson_is_arr(v)) {
        size_t idx, max;
        yyjson_val *itm;
        yyjson_arr_foreach(v, idx, max, itm) {
            char subpath[256];
            snprintf(subpath, sizeof(subpath), "%s[%zu]", path, idx);
            walk(itm, subpath);
        }
    }
}

static int cmp_entry(const void *a, const void *b) {
    size_t sa = ((const Entry *)a)->size;
    size_t sb = ((const Entry *)b)->size;
    return (sb > sa) - (sb < sa);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s file.json [limit]\n", argv[0]);
        return 1;
    }
    int limit = (argc > 2) ? atoi(argv[2]) : 50;

    yyjson_doc *doc = yyjson_read_file(argv[1], 0, NULL, NULL);
    if (!doc) {
        fprintf(stderr, "Failed to parse %s\n", argv[1]);
        return 1;
    }

    yyjson_val *root = yyjson_doc_get_root(doc);
    walk(root, "root");

    qsort(entries, entry_len, sizeof(Entry), cmp_entry);

    if ((size_t)limit > entry_len) limit = (int)entry_len;
    for (int i = 0; i < limit; i++) {
        printf("%10zu  %s\n", entries[i].size, entries[i].path);
    }

    for (size_t i = 0; i < entry_len; i++) free(entries[i].path);
    free(entries);
    yyjson_doc_free(doc);
    return 0;
}
