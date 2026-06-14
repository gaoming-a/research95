from __future__ import annotations

import sys
import tempfile
from pathlib import Path


class DummyDownloader:
    params = {}

    def to_screen(self, message: str) -> None:
        pass

    def report_warning(self, message: str) -> None:
        pass


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    from youtube_dl.postprocessor.ffmpeg import FFmpegSubtitlesConvertorPP
    from youtube_dl.utils import dfxp2srt, subtitles_filename

    dfxp_text = """<?xml version="1.0" encoding="UTF-16"?>
<tt xmlns="http://www.w3.org/ns/ttml">
  <body>
    <div>
      <p begin="0" end="1">Line 1</p>
      <p begin="1" end="2">第二行</p>
    </div>
  </body>
</tt>"""
    expected = """1
00:00:00,000 --> 00:00:01,000
Line 1

2
00:00:01,000 --> 00:00:02,000
第二行

"""

    converted = dfxp2srt(dfxp_text.encode("utf-16"))
    if converted != expected:
        raise AssertionError(f"unexpected direct dfxp2srt output: {converted!r}")

    with tempfile.TemporaryDirectory() as tmp:
        media = str(Path(tmp) / "video.mp4")
        dfxp_path = subtitles_filename(media, "en", "dfxp")
        Path(dfxp_path).write_bytes(dfxp_text.encode("utf-16"))

        info = {
            "filepath": media,
            "requested_subtitles": {"en": {"ext": "dfxp", "data": None}},
        }
        files_to_delete, updated = FFmpegSubtitlesConvertorPP(
            DummyDownloader(), "srt"
        ).run(info)

        srt_path = subtitles_filename(media, "en", "srt")
        if Path(srt_path).read_text(encoding="utf-8") != expected:
            raise AssertionError("converter did not write expected SRT output")
        if updated["requested_subtitles"]["en"]["ext"] != "srt":
            raise AssertionError("converter did not update subtitle extension")
        if updated["requested_subtitles"]["en"]["data"] != expected:
            raise AssertionError("converter did not store expected subtitle data")
        if files_to_delete != [dfxp_path]:
            raise AssertionError(f"unexpected delete list: {files_to_delete!r}")

    print("oracle_passed")


if __name__ == "__main__":
    main()
