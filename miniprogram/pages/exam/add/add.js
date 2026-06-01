const { ExamAPI } = require('../../../utils/api')
Page({
  data: {
    studentId: 0, saving: false,
    subjects: ['语文','数学','英语','科学','道德与法治','其他'],
    subjectIndex: -1,
    form: { subject: '', exam_name: '', score: '', total_score: '', exam_date: new Date().toISOString().slice(0,10) },
    questions: [],
  },
  onLoad(o) { this.setData({ studentId: parseInt(o.studentId) }) },
  onInput(e) { this.setData({ [`form.${e.currentTarget.dataset.field}`]: e.detail.value }) },
  onSubjectChange(e) {
    const index = e.detail.value
    this.setData({ subjectIndex: index, 'form.subject': this.data.subjects[index] })
  },
  onDateChange(e) { this.setData({ 'form.exam_date': e.detail.value }) },
  onAddQuestion() {
    this.setData({ questions: [...this.data.questions, {question:'',student_answer:'',correct_answer:'',score:'',max_score:'',category:''}] })
  },
  onDeleteQuestion(e) {
    this.setData({ questions: this.data.questions.filter((_,i) => i !== e.currentTarget.dataset.index) })
  },
  onQuestionInput(e) {
    const { index, field } = e.currentTarget.dataset
    this.setData({ [`questions[${index}].${field}`]: e.detail.value })
  },
  async onSave() {
    if (!this.data.form.subject) { wx.showToast({ title: '请选择科目', icon: 'none' }); return }
    this.setData({ saving: true })
    const result = await ExamAPI.create({
      student_id: this.data.studentId,
      subject: this.data.form.subject,
      exam_name: this.data.form.exam_name || null,
      score: parseFloat(this.data.form.score) || null,
      total_score: parseFloat(this.data.form.total_score) || null,
      exam_date: this.data.form.exam_date,
      questions: this.data.questions.filter(q => q.question).map(q => ({
        question: q.question, student_answer: q.student_answer || null,
        correct_answer: q.correct_answer || null,
        is_correct: q.correct_answer && q.student_answer ? q.student_answer.trim() === q.correct_answer.trim() : null,
        score: parseFloat(q.score) || null, max_score: parseFloat(q.max_score) || null, category: q.category || null,
      })),
    })
    this.setData({ saving: false })
    if (result) { wx.showToast({ title: '保存成功' }); wx.navigateBack() }
  },
})
