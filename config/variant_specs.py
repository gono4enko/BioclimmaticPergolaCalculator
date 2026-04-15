VARIANT_SPECS = {
    "B500NEW": {
        "Basic": {
            "250": {
                "lamella": "250 × 46 мм Basic",
                "column": "164 × 164 мм New",
                "beam": "164 × 260 мм",
                "beam_double": "322 × 260 мм",
                "max_overhang": 6.5,
                "pros": ["Экономичная конструкция", "Более низкая цена", "Облегчённая конструкция"],
                "cons": ["Умеренная снеговая нагрузка", "Ограниченная ширина модуля"]
            }
        },
        "Light": {
            "250": {
                "lamella": "250 × 45 мм Light",
                "column": "150 × 150 мм New",
                "beam": "150 × 250 мм",
                "beam_double": "300 × 250 мм",
                "max_overhang": 5.5,
                "pros": ["Самая лёгкая конструкция", "Самая низкая цена"],
                "cons": ["Минимальная снеговая нагрузка", "Минимальная ширина модуля"]
            }
        },
        "Pro": {
            "250": {
                "lamella": "250 × 53 мм Pro",
                "column": "164 × 164 мм New",
                "beam": "164 × 260 мм",
                "beam_double": "322 × 260 мм",
                "max_overhang": 6.5,
                "pros": ["Максимальная снеговая нагрузка", "Максимальная ширина модуля"],
                "cons": ["Более высокая цена"]
            },
            "200": {
                "lamella": "200 × 56 мм Pro",
                "column": "164 × 164 мм New",
                "beam": "164 × 260 мм",
                "beam_double": "322 × 260 мм",
                "max_overhang": 6.85,
                "pros": ["Усиленные ламели", "Максимальный вынос до 8 м"],
                "cons": ["Более высокая цена", "Больше вес конструкции"]
            }
        }
    },
    "B700NEW": {
        "Basic": {
            "250": {
                "lamella": "250 × 46 мм Basic",
                "column": "164 × 164 мм New",
                "beam": "164 × 260 мм",
                "beam_double": "322 × 260 мм",
                "max_overhang": 6.5,
                "pros": ["Экономичная конструкция", "Более низкая цена", "Облегчённая конструкция"],
                "cons": ["Умеренная снеговая нагрузка", "Ограниченная ширина модуля"]
            }
        },
        "Light": {
            "250": {
                "lamella": "250 × 45 мм Light",
                "column": "150 × 150 мм New",
                "beam": "150 × 250 мм",
                "beam_double": "300 × 250 мм",
                "max_overhang": 5.5,
                "pros": ["Самая лёгкая конструкция", "Самая низкая цена"],
                "cons": ["Минимальная снеговая нагрузка", "Минимальная ширина модуля"]
            }
        },
        "Pro": {
            "250": {
                "lamella": "250 × 53 мм Pro",
                "column": "164 × 164 мм New",
                "beam": "164 × 260 мм",
                "beam_double": "322 × 260 мм",
                "max_overhang": 6.5,
                "pros": ["Максимальная снеговая нагрузка", "Максимальная ширина модуля"],
                "cons": ["Более высокая цена"]
            },
            "200": {
                "lamella": "200 × 56 мм Pro",
                "column": "164 × 164 мм New",
                "beam": "164 × 260 мм",
                "beam_double": "322 × 260 мм",
                "max_overhang": 6.85,
                "pros": ["Усиленные ламели", "Максимальный вынос до 8 м"],
                "cons": ["Более высокая цена", "Больше вес конструкции"]
            }
        }
    },
    "B600": {
        "Standard": {
            "PIR": {
                "lamella": "PIR сэндвич-панель 100 мм",
                "column": "164 × 164 мм",
                "beam": "164 × 260 мм",
                "beam_double": "322 × 260 мм",
                "max_overhang": 6.5,
                "pros": ["Максимальная ширина модуля до 5 м", "3 модуля до 15 м"],
                "cons": ["Больший вес конструкции"]
            }
        },
        "Light": {
            "PIR": {
                "lamella": "PIR сэндвич-панель 100 мм",
                "column": "150 × 150 мм",
                "beam": "150 × 250 мм",
                "beam_double": "300 × 250 мм",
                "max_overhang": 5.5,
                "pros": ["Облегчённая конструкция", "Более низкая цена"],
                "cons": ["Ширина модуля до 4 м", "3 модуля до 12 м"]
            }
        }
    }
}

VARIANT_DISPLAY_ORDER = {
    "B500NEW": [
        {"variant": "Basic", "lamella_size": "250", "label": "Basic 250мм"},
        {"variant": "Light", "lamella_size": "250", "label": "Light 250мм"},
        {"variant": "Pro", "lamella_size": "250", "label": "Pro 250мм"},
        {"variant": "Pro", "lamella_size": "200", "label": "Pro 200мм"},
    ],
    "B700NEW": [
        {"variant": "Basic", "lamella_size": "250", "label": "Basic 250мм"},
        {"variant": "Light", "lamella_size": "250", "label": "Light 250мм"},
        {"variant": "Pro", "lamella_size": "250", "label": "Pro 250мм"},
        {"variant": "Pro", "lamella_size": "200", "label": "Pro 200мм"},
    ],
    "B600": [
        {"variant": "Standard", "lamella_size": "PIR", "label": "Standard"},
        {"variant": "Light", "lamella_size": "PIR", "label": "Light"},
    ]
}


def get_variant_options(pergola_type):
    if pergola_type not in VARIANT_DISPLAY_ORDER:
        return []
    result = []
    specs = VARIANT_SPECS.get(pergola_type, {})
    for item in VARIANT_DISPLAY_ORDER[pergola_type]:
        variant = item["variant"]
        ls = item["lamella_size"]
        spec = specs.get(variant, {}).get(ls, {})
        result.append({
            "variant": variant,
            "lamella_size": ls,
            "label": item["label"],
            "lamella": spec.get("lamella", ""),
            "column": spec.get("column", ""),
            "beam": spec.get("beam", ""),
            "beam_double": spec.get("beam_double", ""),
            "max_overhang": spec.get("max_overhang", 0),
            "pros": spec.get("pros", []),
            "cons": spec.get("cons", []),
        })
    return result
