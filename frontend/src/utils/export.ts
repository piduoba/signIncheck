import api from '@/utils/request'

// 导出API
export const exportAPI = {
  // 导出用户Excel
  exportUsersExcel: (role?: string): Promise<Blob> => {
    const params = role ? { role } : {}
    return api.get('/export/users/excel', { 
      params,
      responseType: 'blob'
    })
  },

  // 导出签到记录Excel
  exportAttendanceExcel: (params: {
    session_id?: number
    start_date?: string
    end_date?: string
    course_id?: number
  }): Promise<Blob> => {
    return api.get('/export/attendance/excel', { 
      params,
      responseType: 'blob'
    })
  },

  // 导出签到记录PDF
  exportAttendancePDF: (sessionId: number): Promise<Blob> => {
    return api.get(`/export/attendance/pdf?session_id=${sessionId}`, { 
      responseType: 'blob'
    })
  },

  // 导出统计数据Excel
  exportStatisticsExcel: (params: {
    start_date?: string
    end_date?: string
    teacher_id?: number
  }): Promise<Blob> => {
    return api.get('/export/statistics/excel', { 
      params,
      responseType: 'blob'
    })
  }
}

// 下载文件工具函数
export const downloadFile = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// 导出工具类
export class ExportUtils {
  // 导出用户列表
  static async exportUsers(role?: string) {
    try {
      const blob = await exportAPI.exportUsersExcel(role)
      const filename = `用户列表_${new Date().toISOString().slice(0, 10)}.xlsx`
      downloadFile(blob, filename)
      return true
    } catch (error) {
      console.error('导出用户列表失败:', error)
      throw error
    }
  }

  // 导出签到记录
  static async exportAttendanceRecords(params: {
    session_id?: number
    start_date?: string
    end_date?: string
    course_id?: number
    format?: 'excel' | 'pdf'
  }) {
    try {
      const { format = 'excel', ...queryParams } = params
      
      let blob: Blob
      let filename: string
      
      if (format === 'pdf' && params.session_id) {
        blob = await exportAPI.exportAttendancePDF(params.session_id)
        filename = `签到报告_${new Date().toISOString().slice(0, 10)}.pdf`
      } else {
        blob = await exportAPI.exportAttendanceExcel(queryParams)
        filename = `签到记录_${new Date().toISOString().slice(0, 10)}.xlsx`
      }
      
      downloadFile(blob, filename)
      return true
    } catch (error) {
      console.error('导出签到记录失败:', error)
      throw error
    }
  }

  // 导出统计数据
  static async exportStatistics(params: {
    start_date?: string
    end_date?: string
    teacher_id?: number
  }) {
    try {
      const blob = await exportAPI.exportStatisticsExcel(params)
      const filename = `出勤统计_${new Date().toISOString().slice(0, 10)}.xlsx`
      downloadFile(blob, filename)
      return true
    } catch (error) {
      console.error('导出统计数据失败:', error)
      throw error
    }
  }

  // 批量导出
  static async batchExport(exports: Array<{
    type: 'users' | 'attendance' | 'statistics'
    params?: any
  }>) {
    const results = []
    
    for (const exportItem of exports) {
      try {
        switch (exportItem.type) {
          case 'users':
            await this.exportUsers(exportItem.params?.role)
            break
          case 'attendance':
            await this.exportAttendanceRecords(exportItem.params)
            break
          case 'statistics':
            await this.exportStatistics(exportItem.params)
            break
        }
        results.push({ type: exportItem.type, success: true })
      } catch (error) {
        results.push({ type: exportItem.type, success: false, error })
      }
    }
    
    return results
  }
}

// CSV导出工具（前端实现）
export class CSVExporter {
  static exportToCSV(data: any[], filename: string, headers?: string[]) {
    if (data.length === 0) return
    
    // 如果没有提供headers，使用数据的键作为表头
    const csvHeaders = headers || Object.keys(data[0])
    
    // 构建CSV内容
    const csvContent = [
      csvHeaders.join(','), // 表头
      ...data.map(row => 
        csvHeaders.map(header => {
          const value = row[header] || ''
          // 处理包含逗号的值
          return typeof value === 'string' && value.includes(',') 
            ? `"${value}"` 
            : value
        }).join(',')
      )
    ].join('\n')
    
    // 添加BOM以支持中文
    const BOM = '\uFEFF'
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
    downloadFile(blob, filename.endsWith('.csv') ? filename : `${filename}.csv`)
  }
}

// JSON导出工具
export class JSONExporter {
  static exportToJSON(data: any, filename: string) {
    const jsonStr = JSON.stringify(data, null, 2)
    const blob = new Blob([jsonStr], { type: 'application/json' })
    downloadFile(blob, filename.endsWith('.json') ? filename : `${filename}.json`)
  }
}