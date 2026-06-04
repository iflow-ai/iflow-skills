#!/usr/bin/env python3
"""Pipeline: 对已有知识库直接提交创作任务

用法:
  python3 scripts/pipeline_generate.py --kb "AI论文集" --output-type PDF
  python3 scripts/pipeline_generate.py --kb "竞品分析" --output-type PPT --preset "卡通" --query "对比分析"
  python3 scripts/pipeline_generate.py --kb-id "xxx" --output-type PODCAST --poll-creation

  # v2 新增类型示例：
  python3 scripts/pipeline_generate.py --kb "..." --output-type QUIZ --query "出 10 道难题，难度中等"
  python3 scripts/pipeline_generate.py --kb "..." --output-type GRAPH --query "做张卡通风格的竖版信息图"
  python3 scripts/pipeline_generate.py --kb "..." --output-type TRANSLATION --query "把这个文档翻成日语"
  python3 scripts/pipeline_generate.py --kb "..." --output-type PPT_EDIT --query "..."  # 需要前序 PPT 上下文

  # HHVIDEO（T2V 文生视频，默认）:
  python3 scripts/pipeline_generate.py --kb "..." --output-type HHVIDEO --query "未来城市宣传短片" \\
    --video-ratio 16:9 --video-resolution 1080p --video-duration 10
  # HHVIDEO（I2V 参考帧）:
  python3 scripts/pipeline_generate.py --kb "..." --output-type HHVIDEO --query "让画面动起来" \\
    --video-images "https://cdn.../1.jpg,https://cdn.../2.jpg" --video-image-type reference

适用场景: 知识库已有内容，用户直接说"帮我做个PPT""生成一份报告"，不涉及上传或搜索前置步骤。
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from iflow_common import (
    log, find_kb, submit_creation, poll_creation, output,
    validate_output_type, validate_preset, build_video_config,
)


def main():
    parser = argparse.ArgumentParser(description="对已有知识库直接提交创作任务")
    parser.add_argument("--kb", default="", help="知识库名称")
    parser.add_argument("--kb-id", default="", help="知识库 ID")
    parser.add_argument(
        "--output-type", default="PDF",
        help="生成类型: PDF/DOCX/MARKDOWN/PPT/XMIND/PODCAST/VIDEO/HHVIDEO/QUIZ/GRAPH/TRANSLATION/PPT_EDIT"
    )
    parser.add_argument("--query", default="", help="创作要求")
    parser.add_argument("--preset", default="", help="PPT 风格: 商务/卡通（仅 PPT 有效）")

    # HHVIDEO 专属参数（仅 --output-type HHVIDEO 时生效）
    parser.add_argument("--video-images", default="",
                        help="HHVIDEO 参考图片 URL，逗号分隔；空 = T2V 文生视频")
    parser.add_argument("--video-ratio", default="16:9", choices=["16:9", "9:16", "1:1"],
                        help="HHVIDEO 宽高比，默认 16:9，仅 T2V 模式生效")
    parser.add_argument("--video-image-type", default="reference",
                        choices=["reference", "first_frame"],
                        help="HHVIDEO 图片用途：reference=百炼 I2V / first_frame=Seed")
    parser.add_argument("--video-resolution", default="720P",
                        choices=["720P", "1080P", "720p", "1080p"],
                        help="HHVIDEO 分辨率，默认 720P（百炼要求大写，小写会自动转）")
    parser.add_argument("--video-duration", type=int, default=5, choices=[5, 10, 15],
                        help="HHVIDEO 时长（秒），默认 5，Seed 模式忽略")

    parser.add_argument("--poll-creation", action="store_true", help="轮询等待创作完成")
    args = parser.parse_args()

    # 参数校验
    args.output_type = validate_output_type(args.output_type)
    validate_preset(args.preset, args.output_type)

    # 组装 HHVIDEO 的 videoConfig（仅 HHVIDEO 时）
    video_config = None
    if args.output_type == "HHVIDEO":
        images = [u.strip() for u in args.video_images.split(",") if u.strip()] if args.video_images else []
        # 友好提示：用户传了 first_frame 但没传 --video-images 会被 build_video_config 拦截，先给个 hint
        if args.video_image_type == "first_frame" and not images:
            log("提示: --video-image-type first_frame（Seed 首帧模式）必须配 --video-images")
        video_config = build_video_config(
            images=images,
            ratio=args.video_ratio,
            image_type=args.video_image_type,
            resolution=args.video_resolution,
            duration=args.video_duration,
        )
    elif args.video_images or args.video_image_type != "reference" or args.video_ratio != "16:9" or args.video_resolution.upper() != "720P" or args.video_duration != 5:
        log("警告: --video-* 参数仅在 --output-type HHVIDEO 时生效，当前已忽略")

    kb_id = find_kb(args.kb or None, args.kb_id or None)
    log(f"知识库 ID: {kb_id}")

    # 提交创作任务
    creation_id = submit_creation(
        kb_id,
        output_type=args.output_type,
        query=args.query or None,
        preset=args.preset or None,
        video_config=video_config,
    )

    result = {
        "collectionId": kb_id,
        "creationId": creation_id,
        "creationStatus": "submitted" if creation_id else "failed",
    }

    if creation_id and args.poll_creation:
        status = poll_creation(kb_id, creation_id)
        result["creationStatus"] = status

    output(result)


if __name__ == "__main__":
    main()
