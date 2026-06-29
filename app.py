from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# السطر ده مهم جداً عشان Vercel يلقط التطبيق كـ Serverless Function
app = app


def get_student_result(seat_no):
    excel_file = 'results.xlsx'

    if not os.path.exists(excel_file):
        return None, "ملف البيانات results.xlsx غير موجود على السيرفر."

    try:
        df = pd.read_excel(excel_file)

        # تنظيف أسماء الأعمدة من المسافات
        df.columns = df.columns.str.strip()

        # قفش عمود رقم الجلوس تلقائياً مهما كان اسمه
        seat_col = None
        for col in df.columns:
            if 'جلوس' in col or 'seat' in col.lower():
                seat_col = col
                break

        if not seat_col:
            return None, "لم يتم العثور على عمود رقم الجلوس في ملف الإكسيل. تأكد من وجود كلمة (رقم الجلوس) في أول صف."

        # تحويل العمود لنص للبحث المظبوط
        df[seat_col] = df[seat_col].astype(str).str.strip()
        student_data = df[df[seat_col] == str(seat_no).strip()]

        if student_data.empty:
            return None, "رقم الجلوس غير صحيح أو غير موجود."

        row = student_data.iloc[0]

        # قفش عمود الاسم والـ GPA تلقائياً
        name_col = next((c for c in df.columns if 'اسم' in c or 'name' in c.lower()), df.columns[1])
        gpa_col = next((c for c in df.columns if 'المعدل' in c or 'gpa' in c.lower() or 'التقدير العام' in c), None)
        status_col = next((c for c in df.columns if 'حالة' in c or 'الحالة' in c or 'status' in c.lower()), None)

        result = {
            'seat_no': row[seat_col],
            'student_name': row[name_col],
            'gpa': row[gpa_col] if gpa_col else 'غير متوفر',
            'status': str(row[status_col]).strip() if status_col else 'ناجح'
        }

        # إضافة باقي المواد تلقائياً
        for col in df.columns:
            if col not in [seat_col, name_col, gpa_col, status_col]:
                result[col] = str(row[col]).strip()

        return result, None

    except Exception as e:
        return None, f"حدث خطأ أثناء قراءة ملف البيانات: {str(e)}"


@app.route('/', methods=['GET', 'POST'])
def index():
    searched = False
    result = None
    error_msg = None

    if request.method == 'POST':
        searched = True
        seat_no = request.form.get('seat_no')
        if seat_no:
            result, error_msg = get_student_result(seat_no)
        else:
            error_msg = "برجاء إدخال رقم جلوس صالح."

    return render_template('index.html', searched=searched, result=result, error_msg=error_msg)


if __name__ == '__main__':
    app.run(debug=True)