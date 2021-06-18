def diff_schedule_embed_dicts(old_embed: dict, new_embed: dict) -> str:
    """Takes 2 schedule embed dicts and returns a string containing the differences"""
    diffs = []

    # old_embed can be empty if we have reset it, new_embed will always have a title.
    if old_embed.get("title", "") != new_embed["title"]:
        diffs += ["title"]

    if old_embed.get("description", "") != new_embed.get("description", ""):
        diffs += ["description"]

    if old_embed.get("thumbnail", None) != new_embed.get("thumbnail", None):
        diffs += ["thumbnail"]

    if old_embed.get("image", None) != new_embed.get("image", None):
        diffs += ["image"]

    # Dict of name:value for old_embed fields.
    old_embed_fields = {
        field["name"]: field["value"] for field in old_embed.get("fields", [])
    }

    # This detects all field changes except if old_embed has a field that new_embed
    # does not (e.g. a payload was removed). Not going to worry about this for now as
    # it's unlikely to happen.
    # TODO: Detect field removals.
    for field in new_embed.get("fields", []):
        name = field["name"]
        if name in old_embed_fields:
            if old_embed_fields[name] != field["value"]:
                diffs += [name]
        else:
            diffs += [name]

    if len(diffs) == 0:
        return ""
    if len(diffs) == 1:
        return f"Changed: {diffs[0]}"
    return f"Changed: {diffs[0]} + {len(diffs)-1} more"
