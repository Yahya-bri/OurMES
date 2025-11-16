<template>
  <div class="production">
    <h1>Production Tracking & Counting</h1>
    
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ activeOrders }}</div>
          <div class="stat-label">Active Orders</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ activeOperations }}</div>
          <div class="stat-label">Active Operations</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ workstations }}</div>
          <div class="stat-label">Workstations</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ productionLines }}</div>
          <div class="stat-label">Production Lines</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ scheduledTodayCount }}</div>
          <div class="stat-label">Scheduled Today</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ scheduleRunningCount }}</div>
          <div class="stat-label">Running (Scheduled)</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ scheduleOverdueCount }}</div>
          <div class="stat-label">Overdue Tasks</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ scheduleAdherenceRate }}%</div>
          <div class="stat-label">Schedule Adherence</div>
        </el-card>
      </el-col>
    </el-row>

    <el-alert
      title="Operator actions (clock-in/out, quantity entry) now happen from the Operator Console. This view is read-only."
      type="info"
      show-icon
      class="info-banner"
    />

    <el-card style="margin-top: 20px;">
      <template #header>
        <span>Orders in Production</span>
      </template>
      <el-table :data="ordersInProduction" style="width: 100%;" v-loading="loading" @row-click="viewOrderDetails">
        <el-table-column prop="number" label="Order Number" width="130" />
        <el-table-column prop="name" label="Order Name" width="200" />
        <el-table-column prop="product_name" label="Product" width="150" />
        <el-table-column prop="planned_quantity" label="Planned" width="100" />
        <el-table-column prop="done_quantity" label="Produced" width="100">
          <template #default="scope">
            <span :style="{ color: scope.row.done_quantity >= scope.row.planned_quantity ? '#67c23a' : '#606266' }">
              {{ scope.row.done_quantity || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Progress" width="180">
          <template #default="scope">
            <el-progress 
              :percentage="calculateProgress(scope.row)" 
              :status="getProgressStatus(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150">
          <template #default="scope">
            <el-button size="small" type="primary" @click.stop="viewOrderDetails(scope.row)">Details</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>Scheduled Operations</span>
          <el-button text size="small" :loading="scheduleLoading" @click="refreshScheduleData">Sync Schedule</el-button>
        </div>
      </template>
      <el-table
        :data="scheduledOperationRows"
        style="width: 100%;"
        v-loading="scheduleLoading"
        empty-text="No schedule items for active orders"
        class="schedule-table"
      >
        <el-table-column label="Order" width="200">
          <template #default="scope">
            <div class="order-cell">
              <span class="order-number">{{ scope.row.orderNumber }}</span>
              <span class="order-name">{{ scope.row.orderName }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Operation" width="220">
          <template #default="scope">
            <div class="operation-cell">
              <span>{{ scope.row.operationName }}</span>
              <span class="secondary-text" v-if="scope.row.operationNumber">Op {{ scope.row.operationNumber }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Planned" width="220">
          <template #default="scope">
            <div>{{ formatDateTime(scope.row.plannedStart) }}</div>
            <div class="secondary-text">{{ formatDateTime(scope.row.plannedEnd) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="140">
          <template #default="scope">
            <el-tag :type="getScheduleTagType(scope.row.status)">
              {{ getScheduleStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actual / Qty" width="220">
          <template #default="scope">
            <div v-if="scope.row.record">
              <div>{{ scope.row.record.start_time ? formatDateTime(scope.row.record.start_time) : '—' }}</div>
              <div class="secondary-text">
                {{ scope.row.record.produced_quantity || 0 }} good / {{ scope.row.record.scrap_quantity || 0 }} scrap
              </div>
            </div>
            <span v-else>Not started</span>
          </template>
        </el-table-column>
        <el-table-column label="Variance" width="140">
          <template #default="scope">
            <el-tag :type="getDelayTagType(scope.row.delayMinutes)">
              {{ formatDelay(scope.row.delayMinutes) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Details" width="120">
          <template #default="scope">
            <el-button 
              size="small" 
              text 
              @click.stop="viewOrderDetailsById(scope.row.order)"
            >
              View
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Active Operations -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>Active Operations</span>
      </template>
      <el-table :data="activeProductionRecords" style="width: 100%;">
        <el-table-column prop="order_number" label="Order" width="120" />
        <el-table-column label="Operation" width="180">
          <template #default="scope">
            {{ scope.row.operation_name || `Op #${scope.row.operation}` }}
          </template>
        </el-table-column>
        <el-table-column prop="workstation_name" label="Workstation" width="150" />
        <el-table-column prop="start_time" label="Started" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="produced_quantity" label="Produced" width="100" />
        <el-table-column prop="scrap_quantity" label="Scrap" width="100" />
        <el-table-column label="Duration" width="120">
          <template #default="scope">
            {{ calculateDuration(scope.row.start_time) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Workstation Status</span>
          </template>
          <el-empty v-if="!workstationsList.length" description="No workstations available" />
          <div v-else>
            <div v-for="ws in workstationsList" :key="ws.id" class="workstation-item">
              <span>{{ ws.name }}</span>
              <el-tag :type="ws.active ? 'success' : 'info'">
                {{ ws.active ? 'Active' : 'Inactive' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Production Lines</span>
          </template>
          <el-empty v-if="!productionLinesList.length" description="No production lines available" />
          <div v-else>
            <div v-for="line in productionLinesList" :key="line.id" class="production-line-item">
              <span>{{ line.name }}</span>
              <el-tag :type="line.active ? 'success' : 'info'">
                {{ line.active ? 'Active' : 'Inactive' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Order Details Dialog -->
    <el-dialog v-model="showDetailsDialog" title="Order Production Details" width="800px">
      <div v-if="selectedOrder">
        <h3>{{ selectedOrder.number }} - {{ selectedOrder.name }}</h3>
        <el-descriptions :column="2" border style="margin-top: 20px;">
          <el-descriptions-item label="Product">{{ selectedOrder.product_name }}</el-descriptions-item>
          <el-descriptions-item label="State">
            <el-tag :type="getStateType(selectedOrder.state)">{{ selectedOrder.state }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Planned Qty">{{ selectedOrder.planned_quantity }}</el-descriptions-item>
          <el-descriptions-item label="Produced Qty">{{ orderProgress.produced || 0 }}</el-descriptions-item>
          <el-descriptions-item label="Scrap Qty">{{ orderProgress.scrap || 0 }}</el-descriptions-item>
          <el-descriptions-item label="Yield">
            {{ calculateYield(orderProgress.produced, orderProgress.scrap) }}%
          </el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px;">Production Records</h4>
        <el-table :data="orderProductionRecords" style="width: 100%; margin-top: 10px;">
          <el-table-column prop="operation_name" label="Operation" width="180" />
          <el-table-column prop="workstation_name" label="Workstation" width="150" />
          <el-table-column prop="start_time" label="Started" width="150">
            <template #default="scope">
              {{ formatDateTime(scope.row.start_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="end_time" label="Ended" width="150">
            <template #default="scope">
              {{ scope.row.end_time ? formatDateTime(scope.row.end_time) : 'In progress' }}
            </template>
          </el-table-column>
          <el-table-column prop="produced_quantity" label="Produced" width="100" />
          <el-table-column prop="scrap_quantity" label="Scrap" width="100" />
          <el-table-column prop="status" label="Status" width="120">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'completed' ? 'success' : 'warning'">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="showDetailsDialog = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { getOrders } from '@/modules/orders/services/ordersService';
import { getWorkstations, getProductionLines } from '@/modules/basic-data/services/basicDataService';
import { getSchedulingByOrders } from '@/modules/planning/services/schedulingService';
import { getProductionCounting, getOrderProgress } from '../services/productionCountingService';

const ordersInProduction = ref([]);
const allOrdersList = ref([]);
const workstationsList = ref([]);
const productionLinesList = ref([]);
const activeProductionRecords = ref([]);
const scheduleItems = ref([]);
const productionRecordsIndex = ref({});
const scheduleLoading = ref(false);
const loading = ref(false);
const showDetailsDialog = ref(false);
const selectedOrder = ref(null);
const orderProgress = ref({ produced: 0, scrap: 0 });
const orderProductionRecords = ref([]);

const activeOrders = computed(() => ordersInProduction.value.length);
const activeOperations = computed(() => activeProductionRecords.value.filter(r => r.status === 'in_progress').length);
const workstations = computed(() => workstationsList.value.filter(ws => ws.active).length);
const productionLines = computed(() => productionLinesList.value.filter(pl => pl.active).length);
const ordersIndex = computed(() => {
  const map = new Map();
  allOrdersList.value.forEach(order => map.set(order.id, order));
  return map;
});

const normalizeListResponse = (payload) => {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.results)) return payload.results;
  if (Array.isArray(payload.items)) return payload.items;
  return [];
};

const buildProductionRecordIndex = (records) => {
  const index = {};
  records.forEach((record) => {
    const orderId = record.order;
    if (!orderId) return;
    if (!index[orderId]) {
      index[orderId] = {};
    }
    const assignIfNewer = (key) => {
      if (!key) return;
      const existing = index[orderId][key];
      const recordTime = new Date(record.end_time || record.timestamp || record.start_time || Date.now());
      if (!existing) {
        index[orderId][key] = record;
        return;
      }
      const existingTime = new Date(existing.end_time || existing.timestamp || existing.start_time || Date.now());
      if (recordTime > existingTime) {
        index[orderId][key] = record;
      }
    };
    if (record.operation) {
      assignIfNewer(`op:${record.operation}`);
    }
    if (record.component) {
      assignIfNewer(`comp:${record.component}`);
    }
  });
  return index;
};

const findRecordForSchedule = (item) => {
  const orderRecords = productionRecordsIndex.value[item.order];
  if (!orderRecords) return null;
  if (item.operation_id) {
    const byOp = orderRecords[`op:${item.operation_id}`];
    if (byOp) return byOp;
  }
  if (item.component) {
    const byComp = orderRecords[`comp:${item.component}`];
    if (byComp) return byComp;
  }
  return null;
};

const getScheduleStatus = (item) => {
  const record = findRecordForSchedule(item);
  if (record) {
    if (record.status === 'completed') return 'completed';
    if (record.status === 'in_progress') return 'running';
  }
  if (!item.planned_start) return 'scheduled';
  const plannedStart = new Date(item.planned_start).getTime();
  if (!Number.isNaN(plannedStart) && plannedStart < Date.now()) {
    return 'overdue';
  }
  return 'scheduled';
};

const calculateDelayMinutes = (item, record) => {
  if (!item.planned_start) return 0;
  const plannedDate = new Date(item.planned_start);
  const plannedTime = plannedDate.getTime();
  if (Number.isNaN(plannedTime)) return 0;
  if (record && (record.start_time || record.timestamp)) {
    const actualDate = new Date(record.start_time || record.timestamp);
    const actualTime = actualDate.getTime();
    if (!Number.isNaN(actualTime)) {
      return Math.round((actualTime - plannedTime) / 60000);
    }
  }
  const now = Date.now();
  if (now > plannedTime) {
    return Math.round((now - plannedTime) / 60000);
  }
  return 0;
};

const isSameDay = (dateStr, referenceDate = new Date()) => {
  if (!dateStr) return false;
  const date = new Date(dateStr);
  if (Number.isNaN(date.getTime())) return false;
  return (
    date.getFullYear() === referenceDate.getFullYear() &&
    date.getMonth() === referenceDate.getMonth() &&
    date.getDate() === referenceDate.getDate()
  );
};

const scheduledOperationRows = computed(() => {
  return scheduleItems.value
    .map((item) => {
      const record = findRecordForSchedule(item);
      return {
        id: item.id,
        order: item.order,
        orderNumber: item.order_number,
        orderName: item.order_name,
        plannedStart: item.planned_start,
        plannedEnd: item.planned_end,
        operationName: item.component_name,
        operationNumber: item.operation_number,
        operationId: item.operation_id,
        component: item.component,
        status: getScheduleStatus(item),
        record,
        delayMinutes: calculateDelayMinutes(item, record),
      };
    })
    .sort((a, b) => {
      const timeA = a.plannedStart ? new Date(a.plannedStart).getTime() : Infinity;
      const timeB = b.plannedStart ? new Date(b.plannedStart).getTime() : Infinity;
      const normalizedA = Number.isNaN(timeA) ? Infinity : timeA;
      const normalizedB = Number.isNaN(timeB) ? Infinity : timeB;
      if (normalizedA === normalizedB) return 0;
      return normalizedA - normalizedB;
    });
});

const scheduleStatusCounts = computed(() => {
  const base = { scheduled: 0, running: 0, completed: 0, overdue: 0 };
  scheduledOperationRows.value.forEach((row) => {
    if (base[row.status] === undefined) {
      base[row.status] = 1;
    } else {
      base[row.status] += 1;
    }
  });
  return base;
});

const scheduledTodayCount = computed(() =>
  scheduledOperationRows.value.filter((row) => isSameDay(row.plannedStart)).length
);
const scheduleRunningCount = computed(() => scheduleStatusCounts.value.running || 0);
const scheduleOverdueCount = computed(() => scheduleStatusCounts.value.overdue || 0);
const scheduleAdherenceRate = computed(() => {
  const total = scheduledOperationRows.value.length;
  if (!total) return 0;
  const started = (scheduleStatusCounts.value.running || 0) + (scheduleStatusCounts.value.completed || 0);
  return Math.round((started / total) * 100);
});

const getScheduleTagType = (status) => {
  const map = {
    scheduled: 'info',
    running: 'warning',
    completed: 'success',
    overdue: 'danger',
  };
  return map[status] || 'info';
};

const getScheduleStatusLabel = (status) => {
  const map = {
    scheduled: 'Scheduled',
    running: 'Running',
    completed: 'Completed',
    overdue: 'Overdue',
  };
  return map[status] || status;
};

const getDelayTagType = (minutes) => {
  if (!minutes) return 'success';
  if (minutes < 0) return 'info';
  if (minutes <= 15) return 'warning';
  return 'danger';
};

const formatDelay = (minutes) => {
  if (!minutes) return 'On time';
  const absMinutes = Math.abs(minutes);
  if (absMinutes >= 60) {
    const hours = (absMinutes / 60).toFixed(1);
    return minutes > 0 ? `+${hours}h` : `-${hours}h`;
  }
  return minutes > 0 ? `+${absMinutes}m` : `-${absMinutes}m`;
};

const calculateProgress = (order) => {
  if (!order.planned_quantity || order.planned_quantity === 0) return 0;
  const done = order.done_quantity || 0;
  return Math.min(100, Math.round((done / order.planned_quantity) * 100));
};

const getProgressStatus = (order) => {
  const progress = calculateProgress(order);
  if (progress >= 100) return 'success';
  if (progress >= 75) return '';
  if (progress >= 50) return 'warning';
  return 'exception';
};

const getStateType = (state) => {
  const types = {
    pending: 'warning',
    accepted: 'info',
    in_progress: '',
    completed: 'success',
    declined: 'danger',
  };
  return types[state] || '';
};

const calculateYield = (produced, scrap) => {
  const producedNum = Number(produced) || 0;
  const scrapNum = Number(scrap) || 0;
  const total = producedNum + scrapNum;
  if (total === 0) return 0;
  return Math.round((producedNum / total) * 100);
};

const formatDateTime = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const calculateDuration = (startTime) => {
  if (!startTime) return '';
  const start = new Date(startTime);
  const now = new Date();
  const diff = Math.floor((now - start) / 1000); // seconds
  const hours = Math.floor(diff / 3600);
  const minutes = Math.floor((diff % 3600) / 60);
  return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
};

const viewOrderDetails = async (order) => {
  selectedOrder.value = order;
  try {
    const progressData = await getOrderProgress(order.id);
    const producedQty = Number(progressData?.done_quantity ?? 0) || 0;
    const scrapQty = (progressData?.operations || []).reduce(
      (sum, op) => sum + (Number(op?.scrap_quantity ?? 0) || 0),
      0
    );
    orderProgress.value = {
      ...progressData,
      produced: producedQty,
      scrap: scrapQty,
    };

    const records = await getProductionCounting({ order: order.id });
    orderProductionRecords.value = records.results || records;
    
    showDetailsDialog.value = true;
  } catch (error) {
    ElMessage.error('Failed to load order details');
    console.error(error);
  }
};

const viewOrderDetailsById = (orderId) => {
  const order = ordersIndex.value.get(orderId);
  if (order) {
    viewOrderDetails(order);
  } else {
    ElMessage.warning('Order not available in current list');
  }
};

const loadScheduleForOrders = async (orderIds) => {
  if (!orderIds.length) {
    scheduleItems.value = [];
    productionRecordsIndex.value = {};
    return;
  }
  scheduleLoading.value = true;
  try {
    const [scheduleResponse, productionResponse] = await Promise.all([
      getSchedulingByOrders(orderIds),
      getProductionCounting({ order__in: orderIds.join(',') }),
    ]);
    scheduleItems.value = normalizeListResponse(scheduleResponse);
    const productionRecords = normalizeListResponse(productionResponse);
    productionRecordsIndex.value = buildProductionRecordIndex(productionRecords);
  } catch (error) {
    ElMessage.error('Failed to load schedule data');
    console.error(error);
  } finally {
    scheduleLoading.value = false;
  }
};

const resolveScheduleOrderIds = () => {
  const eligibleStates = new Set(['pending', 'accepted', 'in_progress']);
  return allOrdersList.value
    .filter((order) => eligibleStates.has(order.state))
    .map((order) => order.id);
};

const refreshScheduleData = () => {
  const orderIds = resolveScheduleOrderIds();
  if (orderIds.length === 0) {
    scheduleItems.value = [];
    productionRecordsIndex.value = {};
    return;
  }
  loadScheduleForOrders(orderIds);
};

const loadData = async () => {
  loading.value = true;
  try {
    const [
      ordersData,
      workstationsData,
      linesData,
      activeRecordsData,
    ] = await Promise.all([
      getOrders({}),
      getWorkstations(),
      getProductionLines(),
      getProductionCounting({ status: 'in_progress' }),
    ]);

    const allOrders = normalizeListResponse(ordersData);
    allOrdersList.value = allOrders;
    workstationsList.value = normalizeListResponse(workstationsData);
    productionLinesList.value = normalizeListResponse(linesData);
    activeProductionRecords.value = normalizeListResponse(activeRecordsData);

    // Derive orders considered "in production": state in_progress OR has active production record
    const activeOrderIds = new Set(activeProductionRecords.value.map(r => r.order));
    ordersInProduction.value = allOrders.filter(o => o.state === 'in_progress' || activeOrderIds.has(o.id));

    // Sync schedule + production history for orders we care about
    const trackedOrderIds = resolveScheduleOrderIds();
    await loadScheduleForOrders(trackedOrderIds);
  } catch (error) {
    ElMessage.error('Failed to load production data');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.production {
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

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 10px;
}

.info-banner {
  margin-top: 20px;
}

.workstation-item,
.production-line-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
}

.workstation-item:last-child,
.production-line-item:last-child {
  border-bottom: none;
}

.schedule-table .order-cell,
.schedule-table .operation-cell {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.order-number {
  font-weight: 600;
}

.order-name,
.operation-cell .secondary-text,
.secondary-text {
  font-size: 12px;
  color: #909399;
}
</style>
