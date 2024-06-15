from typing import Any, Callable, Dict, List

from szurubooru import errors, model, rest


def get_serialization_options(ctx: rest.Context) -> List[str]:
    return ctx.get_param_as_list("fields", default=[])


class BaseSerializer:
    _fields = {}  # type: Dict[str, Callable[[model.Base], Any]]

    def serialize(self, options: List[str]) -> Any:
        field_factories = self._serializers()
        if not options:
            options = field_factories.keys()

        return {key: field_factories[key]() for key in options}

    def _serializers(self) -> Dict[str, Callable[[], Any]]:
        raise NotImplementedError()
