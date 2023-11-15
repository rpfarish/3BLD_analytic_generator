import drill_generator


def drill_twists(twist_type):
    """Drills twists: 2f: floating 2-twist, 3: 3-twist, or 3f: floating 3-twist"""
    match twist_type:
        case "2f" | "2":
            drill_generator.main("5")
        case "3":
            drill_generator.main("2")
        case "3f":
            drill_generator.main("3")
