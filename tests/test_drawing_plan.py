from src.build_drawing_plan import style_paths, STYLES

def test_all_visual_styles_have_valid_stroke_paths():
    for style in STYLES:
        paths=style_paths(style,60)
        assert paths
        for item in paths:
            assert item["type"]=="path"
            assert len(item["points"])>=2
            assert item["duration"]>0
            assert item["start"]>=0

def test_styles_have_different_visual_plans():
    counts={style:len(style_paths(style,60)) for style in STYLES}
    assert len(set(counts.values()))>1
