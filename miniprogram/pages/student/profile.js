const { StudentAPI } = require('../../utils/api')

Page({
  data: {
    mode: 'add',
    studentId: null,
    form: {
      name: '',
      grade: '',
      class_name: '',
      school: '',
      parent_name: '',
      parent_phone: '',
    },
    grades: ['一年级','二年级','三年级','四年级','五年级','六年级'],
    gradeIndex: -1,
  },

  onLoad(options) {
    if (options.mode === 'edit' && options.id) {
      this.setData({ mode: 'edit', studentId: parseInt(options.id) })
      wx.setNavigationBarTitle({ title: '编辑资料' })
      this.loadStudent(parseInt(options.id))
    }
  },

  async loadStudent(id) {
    const student = await StudentAPI.get(id)
    if (student) {
      const gradeIndex = this.data.grades.indexOf(student.grade)
      this.setData({
        form: {
          name: student.name,
          grade: student.grade,
          class_name: student.class_name || '',
          school: student.school || '',
          parent_name: student.parent_name || '',
          parent_phone: student.parent_phone || '',
        },
        gradeIndex,
      })
    }
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`form.${field}`]: e.detail.value })
  },

  onGradeChange(e) {
    const index = e.detail.value
    this.setData({
      gradeIndex: index,
      'form.grade': this.data.grades[index],
    })
  },

  async onSave() {
    if (!this.data.form.name) {
      wx.showToast({ title: '请输入学生姓名', icon: 'none' })
      return
    }
    if (!this.data.form.grade) {
      wx.showToast({ title: '请选择年级', icon: 'none' })
      return
    }

    if (this.data.mode === 'add') {
      const result = await StudentAPI.create(this.data.form)
      if (result) {
        wx.showToast({ title: '添加成功' })
        wx.navigateBack()
      }
    } else {
      const result = await StudentAPI.update(this.data.studentId, this.data.form)
      if (result) {
        wx.showToast({ title: '保存成功' })
        wx.navigateBack()
      }
    }
  },

  async onDelete() {
    wx.showModal({
      title: '确认删除',
      content: '删除后所有记录将丢失，确定删除吗？',
      success: async (res) => {
        if (res.confirm) {
          await StudentAPI.delete(this.data.studentId)
          wx.showToast({ title: '已删除' })
          wx.switchTab({ url: '/pages/index/index' })
        }
      },
    })
  },
})
