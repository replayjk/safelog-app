import os
from fpdf import FPDF
import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_pdf(description, image_path, timestamp):
    pdf_dir = "pdf_reports/"
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_filename = f"{timestamp}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_filename)

    # GPT-4를 사용하여 필드 자동 채우기
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "너는 아차사고 사례를 작성하는 전문가입니다. 입력된 사고 내용을 바탕으로 사례명, 발생일시, 발생장소, 발생개요, 설비, 발생원인, 예상피해, 재발방지대책을 자동으로 작성하세요."},
                {"role": "user", "content": f"사고 내용: {description}\n필드를 다음 형식으로 채우세요:\n\n사례명:\n발생일시:\n발생장소:\n발생개요:\n설비:\n발생원인:\n예상피해:\n재발방지대책:"}
            ],
            max_tokens=500,
            temperature=0.7
        )

        generated_text = response.choices[0].message.content.strip()
        sections = {"사례명": "", "발생일시": "", "발생장소": "", "발생개요": "", "설비": "", "발생원인": "", "예상피해": "", "재발방지대책": ""}

        for line in generated_text.splitlines():
            for key in sections.keys():
                if line.startswith(key):
                    sections[key] = line.replace(key + ":", "").strip()

    except Exception as e:
        print(f"GPT 처리 중 오류 발생: {e}")
        return None

    # PDF 파일 생성
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # 폰트 설정 (Nanum Gothic URL 사용)
    pdf.set_font("Arial", size=12)

    # 문서 상단 제목
    pdf.set_font_size(24)
    pdf.cell(0, 15, "아차사고 사례 보고서", ln=True, align="C")
    pdf.ln(10)

    # 기본 정보 테이블
    pdf.set_font_size(12)
    pdf.set_fill_color(240, 240, 240)
    for key, value in sections.items():
        pdf.cell(40, 10, key, border=1, fill=True)
        pdf.cell(0, 10, value, border=1, ln=True)
    pdf.ln(5)

    # 이미지 추가
    if image_path:
        try:
            image_full_path = image_path.strip("/")
            pdf.image(image_full_path, x=15, w=180)
            pdf.ln(85)
        except Exception as e:
            print(f"이미지 추가 중 오류 발생: {e}")

    # PDF 저장
    pdf.output(pdf_path)

    return f"/pdf_reports/{pdf_filename}"
