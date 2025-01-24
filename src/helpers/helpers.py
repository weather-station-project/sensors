def get_bool_from_string(value: str) -> bool:
    return value.lower() in ["true", "t", "1"]


class SingletonMeta(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance

        return cls.__instances[cls]
