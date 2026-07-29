from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence


TAG_SCHEMA_VERSION = 1


class TagRuleError(ValueError):
    """Raised when a tag or group operation violates the tag rules."""


def normalize_tag_name(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"tag name must be str, got {type(value).__name__}")

    name = value.strip()
    if not name:
        raise TagRuleError("tag name cannot be empty")
    if "," in name:
        raise TagRuleError("tag name cannot contain a comma")
    return name


def normalize_tags(tags: str | Iterable[str] | None) -> list[str]:
    """Return ordered, unique, non-empty tag names.

    A string is treated as the CSV-compatible comma-separated representation.
    Iterable inputs are treated as already separated tag names.
    """
    if tags is None:
        return []

    values: Iterable[str]
    if isinstance(tags, str):
        if not tags.strip():
            return []
        values = tags.split(",")
    else:
        try:
            values = iter(tags)
        except TypeError as exc:
            raise TypeError("tags must be a string, an iterable of strings, or None") from exc

    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            raise TypeError(f"tag name must be str, got {type(value).__name__}")
        if not value.strip():
            continue
        name = normalize_tag_name(value)
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result


@dataclass
class ExclusiveTagGroup:
    id: str
    name: str
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.id = str(self.id).strip()
        self.name = str(self.name).strip()
        if not self.id:
            raise TagRuleError("exclusive group id cannot be empty")
        if not self.name:
            raise TagRuleError("exclusive group name cannot be empty")
        self.tags = normalize_tags(self.tags)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "tags": list(self.tags)}


@dataclass
class TagFilter:
    exclusive: dict[str, str] = field(default_factory=dict)
    coexist: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.exclusive = {
            str(group_id).strip(): normalize_tag_name(tag)
            for group_id, tag in self.exclusive.items()
            if str(group_id).strip() and isinstance(tag, str) and tag.strip()
        }
        self.coexist = normalize_tags(self.coexist)

    @property
    def required_tags(self) -> set[str]:
        return set(self.exclusive.values()).union(self.coexist)

    @property
    def is_empty(self) -> bool:
        return not self.exclusive and not self.coexist

    def clear(self):
        self.exclusive.clear()
        self.coexist.clear()

    def matches(self, tags: str | Iterable[str] | None) -> bool:
        return self.required_tags.issubset(set(normalize_tags(tags)))


class TagModel:
    """Pure-Python tag catalog and exclusivity rule manager."""

    schema_version = TAG_SCHEMA_VERSION

    def __init__(
        self,
        exclusive_groups: Sequence[ExclusiveTagGroup | Mapping] | None = None,
        coexist_tags: str | Iterable[str] | None = None,
    ):
        self.exclusive_groups: list[ExclusiveTagGroup] = []
        self.coexist_tags: list[str] = []

        for raw_group in exclusive_groups or []:
            group = raw_group if isinstance(raw_group, ExclusiveTagGroup) else ExclusiveTagGroup(
                id=raw_group.get("id") or self._new_group_id(),
                name=raw_group.get("name", ""),
                tags=raw_group.get("tags", []),
            )
            self._append_group(group)

        for tag in normalize_tags(coexist_tags):
            if tag in self.all_tags:
                raise TagRuleError(f'duplicate tag name: "{tag}"')
            self.coexist_tags.append(tag)

    @staticmethod
    def _new_group_id() -> str:
        return f"group-{uuid.uuid4().hex[:12]}"

    @property
    def all_tags(self) -> list[str]:
        tags = list(self.coexist_tags)
        for group in self.exclusive_groups:
            tags.extend(group.tags)
        return tags

    def _append_group(self, group: ExclusiveTagGroup):
        if any(existing.id == group.id for existing in self.exclusive_groups):
            raise TagRuleError(f'duplicate exclusive group id: "{group.id}"')
        if any(existing.name == group.name for existing in self.exclusive_groups):
            raise TagRuleError(f'duplicate exclusive group name: "{group.name}"')

        existing_tags = set(self.all_tags)
        duplicate = next((tag for tag in group.tags if tag in existing_tags), None)
        if duplicate is not None:
            raise TagRuleError(f'duplicate tag name: "{duplicate}"')
        self.exclusive_groups.append(group)

    def get_group(self, group_id: str) -> ExclusiveTagGroup:
        for group in self.exclusive_groups:
            if group.id == group_id:
                return group
        raise TagRuleError(f'exclusive group not found: "{group_id}"')

    def group_for_tag(self, tag: str) -> ExclusiveTagGroup | None:
        name = normalize_tag_name(tag)
        for group in self.exclusive_groups:
            if name in group.tags:
                return group
        return None

    def add_group(self, name: str, group_id: str | None = None) -> ExclusiveTagGroup:
        group = ExclusiveTagGroup(group_id or self._new_group_id(), name, [])
        self._append_group(group)
        return group

    def rename_group(self, group_id: str, new_name: str):
        name = str(new_name).strip()
        if not name:
            raise TagRuleError("exclusive group name cannot be empty")
        if any(group.id != group_id and group.name == name for group in self.exclusive_groups):
            raise TagRuleError(f'duplicate exclusive group name: "{name}"')
        self.get_group(group_id).name = name

    def delete_group(self, group_id: str):
        group = self.get_group(group_id)
        self.exclusive_groups.remove(group)
        for tag in group.tags:
            if tag not in self.coexist_tags:
                self.coexist_tags.append(tag)

    def add_tag(self, name: str, group_id: str | None = None):
        tag = normalize_tag_name(name)
        if tag in self.all_tags:
            raise TagRuleError(f'duplicate tag name: "{tag}"')
        if group_id is None:
            self.coexist_tags.append(tag)
        else:
            self.get_group(group_id).tags.append(tag)

    def rename_tag(self, old_name: str, new_name: str):
        old_tag = normalize_tag_name(old_name)
        new_tag = normalize_tag_name(new_name)
        if old_tag == new_tag:
            return
        if new_tag in self.all_tags:
            raise TagRuleError(f'duplicate tag name: "{new_tag}"')

        if old_tag in self.coexist_tags:
            index = self.coexist_tags.index(old_tag)
            self.coexist_tags[index] = new_tag
            return

        group = self.group_for_tag(old_tag)
        if group is None:
            raise TagRuleError(f'tag not found: "{old_tag}"')
        group.tags[group.tags.index(old_tag)] = new_tag

    def delete_tag(self, name: str):
        tag = normalize_tag_name(name)
        if tag in self.coexist_tags:
            self.coexist_tags.remove(tag)
            return

        group = self.group_for_tag(tag)
        if group is None:
            raise TagRuleError(f'tag not found: "{tag}"')
        group.tags.remove(tag)

    def move_tag(self, name: str, group_id: str | None):
        tag = normalize_tag_name(name)
        if tag not in self.all_tags:
            raise TagRuleError(f'tag not found: "{tag}"')

        current_group = self.group_for_tag(tag)
        if current_group is not None and current_group.id == group_id:
            return
        destination_group = self.get_group(group_id) if group_id is not None else None

        if current_group is not None:
            current_group.tags.remove(tag)
        else:
            self.coexist_tags.remove(tag)

        if destination_group is None:
            self.coexist_tags.append(tag)
        else:
            destination_group.tags.append(tag)

    def register_existing_tags(self, tags: str | Iterable[str] | None):
        for tag in normalize_tags(tags):
            if tag not in self.all_tags:
                self.coexist_tags.append(tag)

    def validate_file_tags(self, tags: str | Iterable[str] | None) -> list[str]:
        normalized = normalize_tags(tags)
        present = set(normalized)
        conflicts: list[str] = []
        for group in self.exclusive_groups:
            selected = [tag for tag in group.tags if tag in present]
            if len(selected) > 1:
                conflicts.append(group.id)
        return conflicts

    def enforce_file_tags(self, tags: str | Iterable[str] | None) -> list[str]:
        """Normalize tags and keep only the last value from each exclusive group."""
        result: list[str] = []
        for tag in normalize_tags(tags):
            if tag not in self.all_tags:
                self.coexist_tags.append(tag)
            result = self.apply_tag_selection(result, tag, True)
        return result

    def apply_tag_selection(
        self,
        tags: str | Iterable[str] | None,
        tag: str,
        selected: bool = True,
    ) -> list[str]:
        result = normalize_tags(tags)
        name = normalize_tag_name(tag)
        if name not in self.all_tags:
            raise TagRuleError(f'tag not found: "{name}"')

        if not selected:
            return [existing for existing in result if existing != name]

        group = self.group_for_tag(name)
        if group is not None:
            group_tags = set(group.tags)
            result = [existing for existing in result if existing not in group_tags]
        if name not in result:
            result.append(name)
        return result

    @staticmethod
    def rename_in_file_tags(
        tags: str | Iterable[str] | None,
        old_name: str,
        new_name: str,
    ) -> list[str]:
        old_tag = normalize_tag_name(old_name)
        new_tag = normalize_tag_name(new_name)
        return normalize_tags(new_tag if tag == old_tag else tag for tag in normalize_tags(tags))

    @staticmethod
    def remove_from_file_tags(
        tags: str | Iterable[str] | None,
        name: str,
    ) -> list[str]:
        tag = normalize_tag_name(name)
        return [existing for existing in normalize_tags(tags) if existing != tag]

    def to_dict(self) -> dict:
        return {
            "tag_schema_version": self.schema_version,
            "exclusive_groups": [group.to_dict() for group in self.exclusive_groups],
            "coexist_tags": list(self.coexist_tags),
        }

    @classmethod
    def from_dict(cls, data: Mapping | None) -> "TagModel":
        if not isinstance(data, Mapping):
            return cls()

        version = data.get("tag_schema_version", 0)
        if isinstance(version, int) and version > TAG_SCHEMA_VERSION:
            logging.warning(
                "Tag schema version %s is newer than supported version %s; loading best-effort",
                version,
                TAG_SCHEMA_VERSION,
            )

        model = cls()
        raw_groups = data.get("exclusive_groups", []) or []
        if not isinstance(raw_groups, Sequence) or isinstance(raw_groups, (str, bytes)):
            logging.warning("Ignoring invalid exclusive_groups metadata")
            raw_groups = []
        for raw_group in raw_groups:
            try:
                if not isinstance(raw_group, Mapping):
                    raise TagRuleError("exclusive group must be an object")
                model._append_group(ExclusiveTagGroup(
                    id=raw_group.get("id") or model._new_group_id(),
                    name=raw_group.get("name", ""),
                    tags=raw_group.get("tags", []),
                ))
            except (TagRuleError, TypeError) as exc:
                logging.warning("Ignoring invalid exclusive tag group: %s", exc)

        try:
            coexist_tags = normalize_tags(data.get("coexist_tags", []))
        except (TagRuleError, TypeError) as exc:
            logging.warning("Ignoring invalid coexist_tags metadata: %s", exc)
            coexist_tags = []
        for tag in coexist_tags:
            if tag in model.all_tags:
                logging.warning('Ignoring duplicate coexist tag: "%s"', tag)
            else:
                model.coexist_tags.append(tag)
        return model
