<template>
  <div class="spc-page">
    <h1>Statistical Process Control (SPC)</h1>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Process Capability (Cp, Cpk)</span>
          </template>
          <div class="chart-placeholder">
            <!-- In a real app, use a charting library like ECharts or Chart.js -->
            <div class="mock-chart">
              <div class="bar" style="height: 80%; background: #67c23a"></div>
              <div class="bar" style="height: 60%; background: #67c23a"></div>
              <div class="bar" style="height: 90%; background: #f56c6c"></div>
              <div class="bar" style="height: 70%; background: #67c23a"></div>
              <div class="line" style="bottom: 85%">UCL</div>
              <div class="line" style="bottom: 15%">LCL</div>
            </div>
            <p style="text-align: center; margin-top: 10px">
              Diameter Variation (mm)
            </p>
          </div>
          <div class="stats">
            <p>
              <strong>Cp:</strong> 1.33 <el-tag type="success">Good</el-tag>
            </p>
            <p>
              <strong>Cpk:</strong> 1.10 <el-tag type="warning">Monitor</el-tag>
            </p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Real-time Alerts</span>
          </template>
          <el-timeline>
            <el-timeline-item timestamp="10:42 AM" type="danger">
              <h4>Out of Control Limit</h4>
              <p>Machine A - Diameter > 10.05mm</p>
            </el-timeline-item>
            <el-timeline-item timestamp="09:15 AM" type="warning">
              <h4>Trend Detected</h4>
              <p>Machine B - 7 points in a row rising</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.spc-page {
  padding: 20px;
}
.chart-placeholder {
  height: 200px;
  border: 1px dashed #ccc;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  padding: 10px;
}
.mock-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 100%;
  position: relative;
}
.bar {
  width: 20px;
  border-radius: 2px 2px 0 0;
}
.line {
  position: absolute;
  width: 100%;
  border-top: 2px dashed #909399;
  left: 0;
  font-size: 10px;
  color: #909399;
}
.stats {
  margin-top: 20px;
  display: flex;
  justify-content: space-around;
}
</style>
