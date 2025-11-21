<template>
  <div class="inspection-config-page">
    <h1>Inspection Configuration</h1>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>Quality Checkpoints</span>
          <el-button type="primary">Add Checkpoint</el-button>
        </div>
      </template>
      <el-table :data="checkpoints" style="width: 100%">
        <el-table-column prop="operation" label="Operation Step" />
        <el-table-column prop="type" label="Check Type" />
        <el-table-column prop="parameters" label="Parameters" />
        <el-table-column prop="mandatory" label="Mandatory">
          <template #default="scope">
            <el-switch v-model="scope.row.mandatory" disabled />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue";

const checkpoints = ref([
  {
    operation: "CNC Milling",
    type: "Variable Data",
    parameters: "Diameter (10.00 +/- 0.05mm)",
    mandatory: true,
  },
  {
    operation: "Assembly",
    type: "Pass/Fail",
    parameters: "Visual Inspection",
    mandatory: true,
  },
  {
    operation: "Packaging",
    type: "Pass/Fail",
    parameters: "Label Verification",
    mandatory: false,
  },
]);
</script>

<style scoped>
.inspection-config-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
