<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ stats.total }}</div>
          <div class="stat-label">Total Orders</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card pending">
          <div class="stat-number">{{ stats.pending }}</div>
          <div class="stat-label">Pending</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card in-progress">
          <div class="stat-number">{{ stats.in_progress }}</div>
          <div class="stat-label">In Progress</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card completed">
          <div class="stat-number">{{ stats.completed }}</div>
          <div class="stat-label">Completed</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>Recent Orders</span>
          </template>
          <el-table :data="recentOrders" style="width: 100%">
            <el-table-column prop="number" label="Order Number" width="150" />
            <el-table-column prop="name" label="Name" />
            <el-table-column prop="product_name" label="Product" />
            <el-table-column prop="state" label="State">
              <template #default="scope">
                <el-tag :type="getStateType(scope.row.state)">{{ scope.row.state }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>Quick Actions</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/orders/new')">New Order</el-button>
            <el-button @click="$router.push('/products')">View Products</el-button>
            <el-button @click="$router.push('/routing')">Manage Routing</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getOrderStats, getOrders } from '@/modules/orders/services/ordersService';

const stats = ref({
  total: 0,
  pending: 0,
  in_progress: 0,
  completed: 0,
});

const recentOrders = ref([]);

const getStateType = (state) => {
  const types = {
    pending: 'warning',
    in_progress: 'info',
    completed: 'success',
    declined: 'danger',
  };
  return types[state] || '';
};

const loadData = async () => {
  try {
    const statsData = await getOrderStats();
    stats.value = statsData;
    
    const ordersData = await getOrders({ limit: 5 });
    recentOrders.value = ordersData.results || ordersData;
  } catch (error) {
    console.error('Error loading dashboard data:', error);
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

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
}

.stat-card.pending .stat-number {
  color: #E6A23C;
}

.stat-card.in-progress .stat-number {
  color: #409EFF;
}

.stat-card.completed .stat-number {
  color: #67C23A;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 10px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
