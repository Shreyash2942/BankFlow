"""Stable persistence errors exposed to BankFlow service code."""

from typing import Any


class RepositoryError(Exception):
    """Base class for failures at the repository boundary."""


class RepositoryNotFoundError(RepositoryError):
    """The requested persistent entity does not exist."""

    def __init__(self, entity_name: str, identifier: Any) -> None:
        self.entity_name = entity_name
        self.identifier = identifier
        super().__init__(f"{entity_name} was not found for identifier {identifier!r}.")


class RepositoryConflictError(RepositoryError):
    """A write conflicts with the current persistent state."""


class ConcurrentUpdateError(RepositoryConflictError):
    """An account changed after the caller read its version."""


class RepositoryWriteError(RepositoryError):
    """The database rejected a repository write."""


class InvalidRepositoryQueryError(RepositoryError, ValueError):
    """A repository query contains invalid pagination or value parameters."""
