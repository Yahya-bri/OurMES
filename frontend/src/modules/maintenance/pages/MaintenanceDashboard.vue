<template>
  <div class="maintenance-dashboard">
    <h1>Maintenance Operations</h1>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Asset History & Reliability (MTBF)</span>
              <el-button type="primary" @click="logMaintenance"
                >Log Maintenance Activity</el-button
              >
            </div>
          </template>

          <el-table :data="assetHistory" style="width: 100%">
            <el-table-column prop="asset" label="Asset Name" />
            <el-table-column prop="lastFailure" label="Last Failure Date" />
            <el-table-column prop="repairTime" label="Repair Duration (hrs)" />
            <el-table-column prop="technician" label="Technician" />
            <el-table-column label="MTBF (Mean Time Between Failures)">
              <template #default="scope">
                <el-tag effect="dark" type="info"
                  >{{ scope.row.mtbf }} hours</el-tag
                >
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showLogDialog" title="Log Maintenance Activity">
      <el-form :model="logForm" label-width="120px">
        <el-form-item label="Asset">
          <el-select v-model="logForm.asset" placeholder="Select Asset">
            <el-option label="CNC Machine A" value="CNC Machine A" />
            <el-option label="Conveyor Belt 1" value="Conveyor Belt 1" />
          </el-select>
        </el-form-item>
        <el-form-item label="Activity Type">
          <el-select v-model="logForm.type" placeholder="Select Type">
            <el-option label="Repair" value="Repair" />
            <el-option label="Preventive" value="Preventive" />
          </el-select>
        </el-form-item>
        <el-form-item label="Duration (hrs)">
          <el-input-number v-model="logForm.duration" :min="0.5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLogDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveLog">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";

const showLogDialog = ref(false);
const logForm = ref({ asset: "", type: "", duration: 1 });

const assetHistory = ref([
  {
    asset: "CNC Machine A",
    lastFailure: "2023-10-15",
    repairTime: 4,
    technician: "John Doe",
    mtbf: 450,
  },
  {
    asset: "Conveyor Belt 1",
    lastFailure: "2023-11-01",
    repairTime: 2,
    technician: "Jane Smith",
    mtbf: 1200,
  },
  {
    asset: "Hydraulic Press X",
    lastFailure: "2023-09-20",
    repairTime: 8,
    technician: "Mike Ross",
    mtbf: 300,
  },
]);

const logMaintenance = () => {
  showLogDialog.value = true;
};

const saveLog = () => {
  // Mock saving logic
  ElMessage.success("Maintenance activity logged.");
  showLogDialog.value = false;
  // In a real app, this would trigger a recalculation of MTBF
};
</script>

<style scoped>
.maintenance-dashboard {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
