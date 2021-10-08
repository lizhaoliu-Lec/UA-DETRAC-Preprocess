import json
import codecs
import os


def _4to1():
    annotation_dir = 'E:/Datasets/UA-DETRAC/UA-DETRAC-COCO-Format/new_annotations'
    new_annotation_dir = 'E:/Datasets/UA-DETRAC/UA-DETRAC-COCO-Format/1_class_annotations'
    # old_json_name = 'instances_test2021.json'
    # json_name = 'instances_test2021_1class.json'
    old_json_name = 'instances_train2021.json'
    json_name = 'instances_train2021_1class.json'

    if not os.path.exists(new_annotation_dir):
        os.makedirs(new_annotation_dir)

    ann_path = os.path.join(annotation_dir, old_json_name)
    new_ann_path = os.path.join(new_annotation_dir, json_name)

    with open(ann_path, 'r', encoding='utf-8') as f:
        ann_json = json.load(f)

    old_anns = ann_json['annotations']

    # change the categories here
    # generate categories json
    old_categories_json = []
    old_cat2id = {cat: cat_id for cat_id, cat in enumerate(['car', 'bus', 'van', 'others'])}
    old_catId2cat = {cat_id: cat for cat, cat_id in old_cat2id.items()}
    for cat, cat_id in old_cat2id.items():
        old_categories_json.append({
            "supercategory": "vehicle",
            "id": cat_id,
            "name": cat,
        })

    # get new categories here
    new_categories_json = []
    new_cat2id = {cat: cat_id for cat_id, cat in enumerate(['has_car', 'others'])}
    old2new_map = {'car': 'has_car', 'bus': 'has_car', 'van': 'has_car', 'others': 'others'}
    for cat, cat_id in new_cat2id.items():
        new_categories_json.append({
            "supercategory": "vehicle",
            "id": cat_id,
            "name": cat,
        })

    new_anns = []
    for ann in old_anns:
        ann['category_id'] = new_cat2id[old2new_map[old_catId2cat[ann['category_id']]]]
        new_anns.append(ann)

    ann_json['annotations'] = new_anns
    ann_json['categories'] = new_categories_json

    # dump the overall to json
    with codecs.open(new_ann_path, 'w', encoding='utf-8') as f:
        json.dump(ann_json, f, ensure_ascii=False)


if __name__ == '__main__':
    _4to1()
