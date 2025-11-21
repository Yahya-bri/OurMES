<template>
  <div class="dashboard">
    <h1>Plant Manager Dashboard</h1>

    <!-- Production Performance Analysis (KPIs) -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Overall Equipment Effectiveness (OEE)</span>
              <el-tag type="success">Target: 85%</el-tag>
            </div>
          </template>
          <div class="kpi-display">
            <el-progress
              type="dashboard"
              :percentage="oeeValue"
              :color="customColors"
            />
            <div class="kpi-details">
              <p>Availability: {{ oeeBreakdown.availability }}%</p>
              <p>Performance: {{ oeeBreakdown.performance }}%</p>
              <p>Quality: {{ oeeBreakdown.quality }}%</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Total Effective Equipment Performance (TEEP)</span>
              <el-tag type="warning">Target: 75%</el-tag>
            </div>
          </template>
          <div class="kpi-display">
            <el-progress
              type="dashboard"
              :percentage="teepValue"
              :color="customColors"
            />
            <div class="kpi-details">
              <p>Utilization: {{ teepBreakdown.utilization }}%</p>
              <p>OEE: {{ oeeValue }}%</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Resource Capability Analysis -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>Resource Capability Analysis (Committed vs Available)</span>
          </template>
          <el-table :data="resourceCapability" style="width: 100%">
            <el-table-column prop="resource" label="Resource Type" />
            <el-table-column prop="total" label="Total Capacity" />
            <el-table-column prop="committed" label="Committed" />
            <el-table-column prop="available" label="Available" />
            <el-table-column label="Utilization">
              <template #default="scope">
                <el-progress
                  :percentage="
                    Math.round((scope.row.committed / scope.row.total) * 100)
                  "
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Production Orders -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>Recent Production Orders</span>
          </template>
          <el-table :data="recentOrders" style="width: 100%">
            <el-table-column prop="number" label="Order Number" width="150" />
            <el-table-column prop="name" label="Name" />
            <el-table-column prop="product_name" label="Product" />
            <el-table-column prop="state" label="State">
              <template #default="scope">
                <el-tag :type="getStateType(scope.row.state)">{{
                  scope.row.state
                }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getOrders } from "@/modules/orders/services/ordersService";

const oeeValue = ref(78);
const teepValue = ref(65);

const oeeBreakdown = ref({
  availability: 85,
  performance: 92,
  quality: 99,
});

const teepBreakdown = ref({
  utilization: 83,
});

const customColors = [
  { color: "#f56c6c", percentage: 60 },
  { color: "#e6a23c", percentage: 80 },
  { color: "#5cb87a", percentage: 100 },
];

const resourceCapability = ref([
  { resource: "CNC Machines", total: 160, committed: 120, available: 40 },
  { resource: "Assembly Line", total: 320, committed: 280, available: 40 },
  { resource: "Packaging", total: 80, committed: 40, available: 40 },
  { resource: "Personnel", total: 50, committed: 45, available: 5 },
]);

const recentOrders = ref([]);

const getStateType = (state) => {
  const types = {
    pending: "warning",
    in_progress: "info",
    completed: "success",
    declined: "danger",
  };
  return types[state] || "";
};

const loadData = async () => {
  try {
    const ordersData = await getOrders({ limit: 5 });
    recentOrders.value = ordersData.results || ordersData;
  } catch (error) {
    console.error("Error loading dashboard data:", error);
  }
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.mb-4 {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kpi-display {
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.kpi-details {
  text-align: left;
}

.kpi-details p {
  margin: 5px 0;
  font-size: 14px;
  color: #606266;
}
</style>
