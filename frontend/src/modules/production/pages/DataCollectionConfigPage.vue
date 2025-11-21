<template>
  <div class="data-collection-page">
    <h1>Production Data Collection Configuration</h1>
    <p class="subtitle">
      Configure automated data capture from Level 2 (SCADA/PLC) systems.
    </p>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>Data Points</span>
          <el-button type="primary" @click="addPoint">Add Data Point</el-button>
        </div>
      </template>

      <el-table :data="dataPoints" style="width: 100%">
        <el-table-column prop="name" label="Tag Name" />
        <el-table-column prop="source" label="Source (PLC/SCADA)" />
        <el-table-column prop="type" label="Data Type" />
        <el-table-column prop="frequency" label="Collection Freq (ms)" />
        <el-table-column label="Actions">
          <template #default="scope">
            <el-button link type="danger" @click="removePoint(scope.$index)"
              >Remove</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue";

const dataPoints = ref([
  { name: "TEMP_ZONE_1", source: "PLC_01", type: "Float", frequency: 1000 },
  {
    name: "CONVEYOR_SPEED",
    source: "SCADA_MAIN",
    type: "Integer",
    frequency: 500,
  },
]);

const addPoint = () => {
  dataPoints.value.push({
    name: "NEW_TAG",
    source: "PLC_XX",
    type: "Float",
    frequency: 1000,
  });
};

const removePoint = (index) => {
  dataPoints.value.splice(index, 1);
};
</script>

<style scoped>
.data-collection-page {
  padding: 20px;
}
.subtitle {
  color: #666;
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
