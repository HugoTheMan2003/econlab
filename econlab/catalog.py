"""The long-term table of contents. Only controls ORDER and which chapters
appear in the sidebar. Models themselves live in econlab/models/."""

CATALOG: dict[str, list[str]] = {
    "MIKROØKONOMI": [
        "Forbrugerteori",
        "Udbud og efterspørgsel",
        "Produktionsteori",
        "Omkostningsteori",
        "Markedsformer",
        "Eksternaliteter og velfærd",
        "Arbejdsmarked",
    ],
    "MAKROØKONOMI": [
        "Nationalregnskab",
        "Keynesianske modeller",
        "IS-LM",
        "Mundell-Fleming",
        "AD-AS",
        "Solow-modellen",
        "Inflation og arbejdsløshed",
    ],
}
