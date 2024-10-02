from abc import ABC, abstractmethod
from typing import Generic, TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")


class Mapper(ABC, Generic[Input, Output]):
    @abstractmethod
    def map_from(self, param: Input) -> Output:
        pass

    @abstractmethod
    def map_to(self, param: Output) -> Input:
        pass
