from dataclasses import dataclass
from typing import Any, List, TypeVar, Callable, Type, cast

T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]

def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()



@dataclass
class App:
    package_name: str
    name: str

    @staticmethod
    def from_dict(obj: Any) -> 'App':
        assert isinstance(obj, dict)
        package_name = from_str(obj.get("package_name"))
        name = from_str(obj.get("name"))
        return App(package_name, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["package_name"] = from_str(self.package_name)
        result["name"] = from_str(self.name)
        return result


@dataclass
class ESearchResult:
    success: bool
    pages: int
    number_of_results: int
    apps: List[App]

    @staticmethod
    def from_dict(obj: Any) -> 'ESearchResult':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        pages = from_int(obj.get("pages"))
        number_of_results = from_int(obj.get("numberOfResults"))
        apps = from_list(App.from_dict, obj.get("apps"))
        return ESearchResult(success, pages, number_of_results, apps)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        result["pages"] = from_int(self.pages)
        result["numberOfResults"] = from_int(self.number_of_results)
        result["apps"] = from_list(lambda x: to_class(App, x), self.apps)
        return result


def e_search_result_from_dict(s: Any) -> ESearchResult:
    return ESearchResult.from_dict(s)


def e_search_result_to_dict(x: ESearchResult) -> Any:
    return to_class(ESearchResult, x)
