from pathlib import Path

import docx
import yaml


class DocxBatchProcessor:
    def __init__(self, yml_config_file_path: str = None) -> None:
        with open(yml_config_file_path, "r") as f:
            config = yaml.safe_load(f)
        self.dataset_dir = Path(config["dataset_dir"])
        self.output_dir = Path(config["output_dir"])
        self.input_files_extension = config["input_files_extension"]
        self.output_files_extension = config["output_files_extension"]
        self.full_file_names = list(
            self.dataset_dir.glob(f"*{self.input_files_extension}")
        )
        self.short_file_names = [i.name for i in self.full_file_names]
        self.output_full_file_names = [
            self.output_dir.joinpath(
                i[: -len(self.input_files_extension)] + self.output_files_extension
            )
            for i in self.short_file_names
        ]

    def _retrieve_text(self, file_name) -> str:
        try:
            doc = docx.Document(file_name)
            fullText = []
            for para in doc.paragraphs:
                fullText.append(para.text)

            return "\n".join(fullText)
        except Exception:
            print("Failed to retrieve text.")

    def _save_to_new_file_format(self, input_data, output_file_name) -> None:
        try:
            with open(output_file_name, "w", encoding="utf-8") as out:
                out.write(input_data)
        except Exception:
            print("Failed to save to new file format")
        return

    def process_and_save_to_txt(self) -> None:
        for i, j in zip(self.full_file_names, self.output_full_file_names):
            try:
                data = self._retrieve_text(file_name=i)
                self._save_to_new_file_format(
                    input_data=data,
                    output_file_name=j,
                )
            except Exception:
                print("Failed to process files in the designated folder.")
        return


if __name__ == "__main__":
    batch_processor = DocxBatchProcessor(
        yml_config_file_path=r"C:\Work\labour-chatbot-knowledge-base\config\text_data_processing.yml"
    )
    batch_processor.process_and_save_to_txt()
