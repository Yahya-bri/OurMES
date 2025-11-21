<template>
  <div class="material-sync-page">
    <h1>Material Synchronization (e-Kanban)</h1>

    <el-row :gutter="20">
      <el-col :span="6" v-for="card in kanbanCards" :key="card.id">
        <el-card :class="['kanban-card', card.status]">
          <div class="card-content">
            <h3>{{ card.material }}</h3>
            <p>Location: {{ card.location }}</p>
            <p>Bin Capacity: {{ card.capacity }}</p>
            <el-tag :type="getStatusType(card.status)">{{
              card.status
            }}</el-tag>
          </div>
          <div class="card-actions">
            <el-button
              v-if="card.status === 'Full'"
              type="warning"
              size="small"
              @click="triggerReplenishment(card)"
            >
              Consume (Trigger Replenish)
            </el-button>
            <el-button
              v-if="card.status === 'Replenishing'"
              type="success"
              size="small"
              @click="completeReplenishment(card)"
            >
              Restock Complete
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";

const kanbanCards = ref([
  {
    id: 1,
    material: "Bolts M8",
    location: "Assembly Line 1",
    capacity: "500 pcs",
    status: "Full",
  },
  {
    id: 2,
    material: "Washers",
    location: "Assembly Line 1",
    capacity: "1000 pcs",
    status: "Replenishing",
  },
  {
    id: 3,
    material: "Gaskets",
    location: "Assembly Line 2",
    capacity: "200 pcs",
    status: "Full",
  },
  {
    id: 4,
    material: "Lubricant",
    location: "CNC Center",
    capacity: "5 L",
    status: "Empty",
  },
]);

const getStatusType = (status) => {
  const map = {
    Full: "success",
    Replenishing: "warning",
    Empty: "danger",
  };
  return map[status] || "info";
};

const triggerReplenishment = (card) => {
  card.status = "Replenishing";
  ElMessage.warning(`Replenishment signal sent for ${card.material}`);
};

const completeReplenishment = (card) => {
  card.status = "Full";
  ElMessage.success(`${card.material} restocked.`);
};
</script>

<style scoped>
.material-sync-page {
  padding: 20px;
}
.kanban-card {
  margin-bottom: 20px;
  text-align: center;
}
.card-content h3 {
  margin: 0 0 10px 0;
}
.card-actions {
  margin-top: 15px;
}
</style>
