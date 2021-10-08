import codecs
import json
import xml.etree.ElementTree as ET
import os
import time
from PIL import Image
import shutil
import tqdm


def read_xml_annotations(file_name):
    result = {}

    # open xml file
    # file_name = 'E:/Datasets/UA-DETRAC/annotations/DETRAC-Train-Annotations-XML/MVI_20011.xml'

    # sequence node
    sequence = ET.parse(file_name).getroot()
    sequence_attrib = sequence.attrib

    assert sequence.tag == 'sequence'

    # print("===> sequence.tag: {}".format(sequence.tag))
    # print("===> sequence_attrib: {}".format(sequence_attrib))

    result['sequence_name'] = sequence_attrib['name']
    result['objects'] = []

    # frame node
    # frames = sequence.getchildren()
    # traverse every frame
    last_num = None
    for idx, frame in enumerate(sequence):
        frame_results = {}
        if frame.tag == 'sequence_attribute' or frame.tag == 'ignored_region':
            # print("===> {} occur, continue".format(frame.tag))
            continue
        frame_attrib = frame.attrib
        # (1) retrieve the frame number for identify the image name
        # print("===> frame_attrib: {}".format(frame_attrib))
        # print("===> frame_attrib['num']: {}".format(frame_attrib['num']))
        frame_results['frame_num'] = frame_attrib['num']
        # print("===> frame_attrib['num']: {}".format(frame_attrib['num']))
        frame_results['objects'] = []
        target_list = [_ for _ in frame]
        assert len(target_list) == 1
        target_list = target_list[0]
        for target in target_list:
            one_object = {}
            # (2) retrieve every box (e.g., objects) from current frame
            for _idx, _box_or_attr in enumerate(target):
                if _box_or_attr.tag in ['box', 'attribute']:
                    if _box_or_attr.tag == 'box':
                        box_attr = _box_or_attr.attrib
                        one_object['x'] = float(box_attr['left'])
                        one_object['y'] = float(box_attr['top'])
                        one_object['w'] = float(box_attr['width'])
                        one_object['h'] = float(box_attr['height'])
                    if _box_or_attr.tag == 'attribute':
                        attr_attr = _box_or_attr.attrib
                        one_object['category'] = attr_attr['vehicle_type']

            frame_results['objects'].append(one_object)

        result['objects'].append(frame_results)
        # print("idx: {}, frame_attrib['num']: {}".format(idx - 1, frame_attrib['num']))
        # assert idx + 1 == int(frame_attrib['num']), "idx + 1: {}, int(frame_attrib['num']): {}".format(idx + 1,
        #                                                                                                frame_attrib[
        #                                                                                                    'num'])

        # last_num = int(frame_attrib['num'])

    # assert last_num == len(result['objects']), "last_num: {}, len(result['objects']): {}".format(last_num,
    #                                                                                              len(result['objects']))

    # print(result.keys())
    # print(result['sequence_name'])
    # print(len(result['objects']))
    # print(len(result['objects'][0]))
    # print(result['objects'][0])
    # print(result['objects'][2])

    return result


def main():
    # image_base_dir = "E:/Datasets/UA-DETRAC/DETRAC-train-data/Insight-MVT_Annotation_Train"
    # annotation_base_dir = "E:/Datasets/UA-DETRAC/original_annotations/DETRAC-Train-Annotations-XML"
    # new_image_dir = 'E:/Datasets/UA-DETRAC/train2021'
    # new_annotation_dir = 'E:/Datasets/UA-DETRAC/annotations'
    # new_json_name = 'instances_train2021.json'

    image_base_dir = "E:/Datasets/UA-DETRAC/DETRAC-test-data/Insight-MVT_Annotation_Test"
    annotation_base_dir = "E:/Datasets/UA-DETRAC/original_annotations/DETRAC-Test-Annotations-XML"
    new_image_dir = 'E:/Datasets/UA-DETRAC/test2021'
    new_annotation_dir = 'E:/Datasets/UA-DETRAC/annotations'
    new_json_name = 'instances_test2021.json'

    for _ in [new_image_dir, new_annotation_dir]:
        if not os.path.exists(_):
            os.makedirs(_)

    info_json = {
        "description": "UA-DETRAC is a challenging real-world multi-object detection and multi-object tracking benchmark.",
        "url": "https://detrac-db.rit.albany.edu/", "version": "1.0",
        "year": time.strftime("%Y", time.localtime()),
        "contributor": "SMIL",
        "date_created": time.strftime("%Y/%m/%d", time.localtime())
    }
    image_json = []
    annotation_json = []

    image_id = 0
    annotation_id = 0

    # generate categories json
    categories_json = []
    cat2id = {cat: cat_id for cat_id, cat in enumerate(['car', 'bus', 'van', 'others'])}
    for cat, cat_id in cat2id.items():
        categories_json.append({
            "supercategory": "vehicle",
            "id": cat_id,
            "name": cat,
        })

    # iterative the annotation dir
    for xml_file in tqdm.tqdm(os.listdir(annotation_base_dir)):
        xml_file = os.path.join(annotation_base_dir, xml_file)
        # step 1: read annotations
        annotation_results = read_xml_annotations(file_name=xml_file)
        sequence_name = annotation_results['sequence_name']
        print("===> sequence_name: {}".format(sequence_name))
        objects = annotation_results['objects']
        # step 2: read images
        sequence_image_base = os.path.join(image_base_dir, sequence_name)
        expected_length = len(annotation_results['objects'])
        actual_length = len(os.listdir(sequence_image_base))
        # not necessary equal
        # assert expected_length == actual_length, 'expected: {}, actual: {}'.format(expected_length, actual_length)
        for _objects in objects:
            frame_num = _objects['frame_num']
            frame_objects = _objects['objects']

            # record one image
            image_name = 'img{}.jpg'.format(str(frame_num).zfill(5))
            full_image_path = os.path.join(sequence_image_base, image_name)
            assert os.path.exists(full_image_path)

            new_image_name = 'img{}.jpg'.format(str(image_id).zfill(10))
            new_image_path = os.path.join(new_image_dir, new_image_name)

            # copy image to target dir
            shutil.copy(full_image_path, new_image_path)

            # read image and get height and width
            height, width = Image.open(full_image_path).size
            # record multiple annotations of this image
            image_json.append({
                "id": image_id,
                "file_name": new_image_name,
                "height": height,
                "width": width,
                "coco_url": "",
                "iscrowd": 0,
            })

            # step 3: generate coco annotation
            for frame_object in frame_objects:
                annotation_json.append({
                    "id": annotation_id,
                    "image_id": image_id,
                    "segmentation": [],
                    "bbox": [frame_object['x'], frame_object['y'], frame_object['w'], frame_object['h']],
                    "category_id": cat2id[frame_object['category']],  # TODO
                    "area": frame_object['w'] * frame_object['h'],
                })
                annotation_id += 1
            image_id += 1

    # dump the overall to json
    with codecs.open(os.path.join(new_annotation_dir, new_json_name), 'w', encoding='utf-8') as f:
        json.dump({
            "info": info_json,
            "images": image_json,
            "annotations": annotation_json,
            "categories": categories_json,
        }, f, ensure_ascii=False)


if __name__ == '__main__':
    # read_xml_annotations('E:/Datasets/UA-DETRAC/original_annotations/DETRAC-Train-Annotations-XML/MVI_20011.xml')
    # read_xml_annotations('E:/Datasets/UA-DETRAC/original_annotations/DETRAC-Train-Annotations-XML/MVI_39761.xml')
    main()
