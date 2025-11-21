<template>
  <div class="reports-page">
    <h1>Regulatory & Quality Compliance Reporting</h1>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="Compliance Records" name="compliance">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Compliance Records (FDA / ISO)</span>
              <el-button type="primary" @click="generateReport"
                >Generate New Report</el-button
              >
            </div>
          </template>
          <el-table :data="complianceRecords" style="width: 100%">
            <el-table-column prop="id" label="Record ID" width="120" />
            <el-table-column prop="type" label="Type" />
            <el-table-column prop="date" label="Date Generated" />
            <el-table-column prop="status" label="Status">
              <template #default="scope">
                <el-tag
                  :type="
                    scope.row.status === 'Compliant' ? 'success' : 'danger'
                  "
                  >{{ scope.row.status }}</el-tag
                >
              </template>
            </el-table-column>
            <el-table-column label="Actions">
              <template #default>
                <el-button link type="primary">Download</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="Audit Trails" name="audit">
        <el-card>
          <template #header>
            <span>System Audit Trail</span>
          </template>
          <el-table :data="auditTrail" style="width: 100%">
            <el-table-column prop="timestamp" label="Timestamp" width="180" />
            <el-table-column prop="user" label="User" width="150" />
            <el-table-column prop="action" label="Action" />
            <el-table-column prop="details" label="Details" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";

const activeTab = ref("compliance");

const complianceRecords = ref([
  {
    id: "REC-001",
    type: "Batch Record",
    date: "2023-10-25",
    status: "Compliant",
  },
  {
    id: "REC-002",
    type: "Sterilization Log",
    date: "2023-10-26",
    status: "Compliant",
  },
  {
    id: "REC-003",
    type: "Maintenance Log",
    date: "2023-10-27",
    status: "Non-Compliant",
  },
]);

const auditTrail = ref([
  {
    timestamp: "2023-10-27 10:00:00",
    user: "jdoe",
    action: "Login",
    details: "User logged in",
  },
  {
    timestamp: "2023-10-27 10:15:00",
    user: "jdoe",
    action: "Update Recipe",
    details: "Changed temp parameter to 150C",
  },
  {
    timestamp: "2023-10-27 11:30:00",
    user: "asmith",
    action: "Approve Order",
    details: "Approved Order #12345",
  },
]);

const generateReport = () => {
  ElMessage.success("Generating Compliance Report... This may take a moment.");
  // Mock generation delay
  setTimeout(() => {
    complianceRecords.value.unshift({
      id: `REC-00${complianceRecords.value.length + 1}`,
      type: "On-Demand Audit",
      date: new Date().toISOString().split("T")[0],
      status: "Compliant",
    });
    ElMessage.success("Report Generated Successfully");
  }, 1500);
};
</script>

<style scoped>
.reports-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
