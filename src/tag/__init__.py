"""Tag 领域模型与相关 UI。

- schema: 纯 Python 领域模型（TagModel/ExclusiveTagGroup/TagFilter 等）
- panel:  Qt UI 组件（TagPanel/TagManagerDialog）
"""

from .schema import (
    TAG_SCHEMA_VERSION,
    ExclusiveTagGroup,
    TagFilter,
    TagModel,
    TagRuleError,
    normalize_tag_name,
    normalize_tags,
)

__all__ = [
    "TAG_SCHEMA_VERSION",
    "ExclusiveTagGroup",
    "TagFilter",
    "TagModel",
    "TagRuleError",
    "normalize_tag_name",
    "normalize_tags",
]
