import os

from dotenv import load_dotenv

import supervisely as sly

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

workspace_id = sly.env.workspace_id()

api = sly.Api.from_env()

project = api.project.create(workspace_id, "Grouped cars", change_name_if_conflict=True)
dataset = api.dataset.create(project.id, "ds0")

# enable multiview settings for project
api.project.set_multiview_settings(project.id)

# ======================================================================================
# ======================================================================================
# ======================================================================================
# OPTION 1: upload images as a group (recommended)

for group_dir in os.scandir("src/images"):
    if not group_dir.is_dir():
        continue
    images_paths = sly.fs.list_files(group_dir.path, valid_extensions=sly.image.SUPPORTED_IMG_EXTS)

    api.image.upload_multiview_images(dataset.id, group_dir.name, images_paths)

# ======================================================================================
# ======================================================================================
# ======================================================================================
# OPTION 2: upload images, add tags

# get project meta from server and tag meta (we will need it later)
project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project.id))
tag_meta = project_meta.get_tag_meta("multiview")

# upload images to Supervisely
for group_dir in os.scandir("src/images"):
    if not group_dir.is_dir():
        continue
    images_paths = sly.fs.list_files(group_dir.path, valid_extensions=sly.image.SUPPORTED_IMG_EXTS)
    images_names = [os.path.basename(img_path) for img_path in images_paths]
    images_infos = api.image.upload_paths(dataset.id, images_names, images_paths)
    images_ids = [image_info.id for image_info in images_infos]
    api.image.add_tag_batch(images_ids, tag_meta.sly_id, value=group_dir.name)
