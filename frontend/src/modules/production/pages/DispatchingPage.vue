<template>
  <div class="dispatching-page">
    <h1>Production Dispatching</h1>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="work-center-list">
          <template #header>
            <span>Work Centers</span>
          </template>
          <el-menu default-active="1" @select="handleWorkCenterSelect">
            <el-menu-item index="1">
              <el-icon><Setting /></el-icon>
              <span>CNC Machining Center A</span>
            </el-menu-item>
            <el-menu-item index="2">
              <el-icon><Setting /></el-icon>
              <span>Assembly Line 1</span>
            </el-menu-item>
            <el-menu-item index="3">
              <el-icon><Setting /></el-icon>
              <span>Packaging Station</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Job Queue: {{ selectedWorkCenter }}</span>
              <el-button type="primary" size="small" @click="assignJob"
                >Assign Job</el-button
              >
            </div>
          </template>

          <el-table :data="jobQueue" style="width: 100%">
            <el-table-column prop="priority" label="Priority" width="80" />
            <el-table-column prop="jobId" label="Job ID" width="120" />
            <el-table-column prop="product" label="Product" />
            <el-table-column prop="status" label="Status">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{
                  scope.row.status
                }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Actions">
              <template #default="scope">
                <el-button size="small" @click="moveUp(scope.$index)"
                  >↑</el-button
                >
                <el-button size="small" @click="moveDown(scope.$index)"
                  >↓</el-button
                >
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { Setting } from "@element-plus/icons-vue";

const selectedWorkCenter = ref("CNC Machining Center A");
const jobQueue = ref([
  {
    priority: 1,
    jobId: "JOB-1001",
    product: "Gear Shaft X",
    status: "Running",
  },
  { priority: 2, jobId: "JOB-1004", product: "Housing Y", status: "Queued" },
  { priority: 3, jobId: "JOB-1009", product: "Flange Z", status: "Queued" },
]);

const handleWorkCenterSelect = (index) => {
  const centers = {
    1: "CNC Machining Center A",
    2: "Assembly Line 1",
    3: "Packaging Station",
  };
  selectedWorkCenter.value = centers[index];
};

const getStatusType = (status) => {
  return status === "Running" ? "success" : "info";
};

const moveUp = (index) => {
  if (index > 0) {
    const item = jobQueue.value.splice(index, 1)[0];
    jobQueue.value.splice(index - 1, 0, item);
    updatePriorities();
  }
};

const moveDown = (index) => {
  if (index < jobQueue.value.length - 1) {
    const item = jobQueue.value.splice(index, 1)[0];
    jobQueue.value.splice(index + 1, 0, item);
    updatePriorities();
  }
};

const updatePriorities = () => {
  jobQueue.value.forEach((job, idx) => {
    job.priority = idx + 1;
  });
};

const assignJob = () => {
  // Logic to assign a new job manually
  console.log("Assign job clicked");
};
</script>

<style scoped>
.dispatching-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
