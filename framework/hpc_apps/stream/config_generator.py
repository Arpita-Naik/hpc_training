def generate_stream_env(cfg):
    return {
        "OMP_NUM_THREADS": cfg["runtime"]["threads"],
        "STREAM_ARRAY_SIZE": cfg["problem"]["array_size"],
        "NTIMES": cfg["problem"]["ntimes"]
    }