<template>
  <div class="operator-panel">
    <h1>Operator Console</h1>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Workstation & Operator</span>
              <el-button
                text
                size="small"
                @click="refreshWorkstationData"
                :disabled="!selectedWorkstation"
                :loading="scheduleLoading"
              >
                Refresh
              </el-button>
            </div>
          </template>

          <el-form label-position="top">
            <el-form-item label="Production Line">
              <el-select
                v-model="selectedProductionLine"
                placeholder="Select production line"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="line in productionLineOptions"
                  :key="line.id"
                  :label="line.label"
                  :value="line.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="Workstation">
              <el-select
                v-model="selectedWorkstation"
                placeholder="Select workstation"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="ws in workstationOptions"
                  :key="ws.id"
                  :label="ws.label"
                  :value="ws.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="Operator">
              <el-select
                v-model="selectedOperator"
                placeholder="Select operator"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="op in operatorOptions"
                  :key="op.id"
                  :label="op.label"
                  :value="op.id"
                />
              </el-select>
            </el-form-item>
          </el-form>

          <el-alert
            v-if="!selectedWorkstation"
            type="warning"
            show-icon
            title="Pick a workstation to load the queue."
          />
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="active-card">
          <template #header>
            <span>Active Operation</span>
          </template>
          <div v-if="activeRecord" class="active-details">
            <div class="detail-grid">
              <div>
                <label>Order</label>
                <div>
                  {{ activeRecord.order_number }} ·
                  {{ activeRecord.product_name }}
                </div>
              </div>
              <div>
                <label>Operation</label>
                <div>
                  {{
                    activeRecord.operation_name || activeRecord.operation_number
                  }}
                </div>
              </div>
              <div>
                <label>Started</label>
                <div>{{ formatDateTime(activeRecord.start_time) }}</div>
              </div>
              <div>
                <label>Operator</label>
                <div>{{ activeRecord.operator_name || "—" }}</div>
              </div>
            </div>
            <div class="active-actions">
              <el-tag type="warning">Running</el-tag>
              <el-button type="danger" @click="openClockOutDialog(activeRecord)"
                >Clock Out</el-button
              >
              <el-button type="info" @click="reportMaintenance"
                >Report Downtime</el-button
              >
            </div>
          </div>
          <el-empty
            v-else
            description="No operation is running on this workstation."
          />
        </el-card>

        <!-- Work Instructions -->
        <el-card class="mt-4" v-if="activeRecord">
          <template #header>
            <span>Work Instructions (Work Directives)</span>
          </template>
          <div class="instructions-content">
            <el-steps direction="vertical" :active="1">
              <el-step
                title="Preparation"
                description="Check material availability and safety gear."
              />
              <el-step
                title="Execution"
                description="Run the machine at specified parameters (Temp: 150C)."
              />
              <el-step
                title="Quality Check"
                description="Measure diameter and record value (Target: 10.00mm)."
              />
              <el-step
                title="Inspection"
                description="Verify product quality against sample."
              />
            </el-steps>
            <div class="safety-alert">
              <el-alert
                title="Safety: Wear protective eyewear at all times."
                type="error"
                show-icon
                :closable="false"
              />
            </div>
          </div>
        </el-card>

        <!-- Work Alerts -->
        <el-card class="mt-4" v-if="activeRecord">
          <template #header>
            <span>Active Alerts</span>
          </template>
          <el-alert
            title="Temperature deviation detected (+5%)"
            type="warning"
            show-icon
            class="mb-2"
          />
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="queue-header">
          <span>Scheduled Operations Queue</span>
          <el-tag v-if="selectedWorkstationName" type="info">
            {{ selectedWorkstationName }}
          </el-tag>
        </div>
      </template>

      <el-empty
        v-if="!selectedWorkstation"
        description="Select a workstation to load its queue."
      />
      <el-table
        v-else
        :data="pendingTasks"
        v-loading="scheduleLoading"
        style="width: 100%"
        class="queue-table"
        empty-text="No pending tasks for this workstation."
      >
        <el-table-column label="Order" width="180">
          <template #default="scope">
            <div class="order-cell">
              <span class="order-number">{{ scope.row.orderNumber }}</span>
              <span class="secondary-text">{{ scope.row.productName }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Operation" width="220">
          <template #default="scope">
            <div class="operation-cell">
              <span>{{ scope.row.operationName }}</span>
              <span class="secondary-text"
                >Op {{ scope.row.operationNumber }}</span
              >
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Planned Window" width="220">
          <template #default="scope">
            <div>{{ formatDateTime(scope.row.plannedStart) }}</div>
            <div class="secondary-text">
              {{ formatDateTime(scope.row.plannedEnd) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="140">
          <template #default="scope">
            <el-tag :type="getStatusTag(scope.row.status)">
              {{ formatStatus(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Action" width="140">
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              @click="clockIn(scope.row)"
              :disabled="clockInDisabled || scope.row.status !== 'scheduled'"
            >
              Clock In
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showClockOutDialog" title="Clock Out" width="420px">
      <el-form :model="clockOutForm" label-width="140px">
        <el-form-item label="Produced Quantity">
          <el-input-number
            v-model="clockOutForm.produced_quantity"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Scrap Quantity">
          <el-input-number
            v-model="clockOutForm.scrap_quantity"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showClockOutDialog = false">Cancel</el-button>
        <el-button type="success" @click="handleClockOut">Clock Out</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { ElMessage } from "element-plus";
import {
  getWorkstations,
  getStaff,
} from "@/modules/basic-data/services/basicDataService";
import { getScheduling } from "@/modules/planning/services/schedulingService";
import {
  getProductionCounting,
  startOperation as apiStartOperation,
  stopOperation as apiStopOperation,
} from "../services/productionCountingService";

const workstations = ref([]);
const staffList = ref([]);
const selectedProductionLine = ref(null);
const selectedWorkstation = ref(null);
const selectedOperator = ref(null);
const scheduleItems = ref([]);
const scheduleLoading = ref(false);
const activeRecord = ref(null);
const completedRecordIndex = ref({});
const showClockOutDialog = ref(false);
const clockOutForm = ref({
  produced_quantity: 0,
  scrap_quantity: 0,
});
const clockOutTarget = ref(null);

const productionLineOptions = computed(() => {
  const map = new Map();
  workstations.value.forEach((ws) => {
    if (ws.production_line && !map.has(ws.production_line)) {
      map.set(ws.production_line, {
        id: ws.production_line,
        label: ws.production_line_name || `Line ${ws.production_line}`,
      });
    }
  });
  return Array.from(map.values());
});

const workstationOptions = computed(() =>
  workstations.value
    .filter((ws) => {
      if (!selectedProductionLine.value) return true;
      return ws.production_line === selectedProductionLine.value;
    })
    .map((ws) => ({
      id: ws.id,
      label: ws.production_line_name
        ? `${ws.name} (${ws.production_line_name})`
        : ws.name,
      productionLine: ws.production_line,
    }))
);

const operatorOptions = computed(() =>
  staffList.value.map((st) => ({
    id: st.id,
    label: `${st.number} - ${st.name} ${st.surname}`,
  }))
);

const selectedWorkstationName = computed(() => {
  const current = workstations.value.find(
    (ws) => ws.id === selectedWorkstation.value
  );
  return current ? current.name : "";
});

const selectedWorkstationLine = computed(() => {
  const current = workstations.value.find(
    (ws) => ws.id === selectedWorkstation.value
  );
  return current?.production_line || null;
});

const clockInDisabled = computed(() => {
  if (!selectedWorkstation.value || !selectedOperator.value) return true;
  return Boolean(activeRecord.value);
});

const scheduledTasks = computed(() => {
  return scheduleItems.value
    .map((item) => {
      const status = deriveTaskStatus(item);
      return {
        id: item.id,
        order: item.order,
        orderNumber: item.order_number,
        productName: item.product_name,
        operationName: item.component_name,
        operationNumber: item.operation_number,
        operationId: item.operation_id,
        component: item.component,
        plannedStart: item.planned_start,
        plannedEnd: item.planned_end,
        status,
        productionLineId: item.production_line,
        productionLineName: item.production_line_name,
      };
    })
    .sort(
      (a, b) => new Date(a.plannedStart || 0) - new Date(b.plannedStart || 0)
    );
});

const pendingTasks = computed(() =>
  scheduledTasks.value.filter((task) => {
    if (task.status === "completed") return false;
    if (!selectedWorkstationLine.value || !task.productionLineId) return true;
    return task.productionLineId === selectedWorkstationLine.value;
  })
);

const normalizeListResponse = (payload) => {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.results)) return payload.results;
  if (Array.isArray(payload.items)) return payload.items;
  return [];
};

const buildCompletedIndex = (records) => {
  const index = {};
  records.forEach((record) => {
    if (record.component) {
      const existing = index[record.component];
      if (!existing) {
        index[record.component] = record;
        return;
      }
      const existingTime = new Date(
        existing.end_time || existing.timestamp || 0
      ).getTime();
      const incomingTime = new Date(
        record.end_time || record.timestamp || 0
      ).getTime();
      if (incomingTime > existingTime) {
        index[record.component] = record;
      }
    }
  });
  return index;
};

const deriveTaskStatus = (item) => {
  if (activeRecord.value && activeRecord.value.component === item.component) {
    return "running";
  }
  if (completedRecordIndex.value[item.component]) {
    return "completed";
  }
  return "scheduled";
};

const getStatusTag = (status) => {
  const map = {
    scheduled: "info",
    running: "warning",
    completed: "success",
  };
  return map[status] || "info";
};

const formatStatus = (status) => {
  const labels = {
    scheduled: "Scheduled",
    running: "Running",
    completed: "Completed",
  };
  return labels[status] || status;
};

const formatDateTime = (value) => {
  if (!value) return "—";
  return new Date(value).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const loadLookups = async () => {
  try {
    const [wsData, staffData] = await Promise.all([
      getWorkstations({ active: true }),
      getStaff({ active: true }),
    ]);
    workstations.value = normalizeListResponse(wsData);
    staffList.value = normalizeListResponse(staffData);
    if (!selectedProductionLine.value && productionLineOptions.value.length) {
      selectedProductionLine.value = productionLineOptions.value[0].id;
    }
    if (!selectedWorkstation.value && workstationOptions.value.length) {
      selectedWorkstation.value = workstationOptions.value[0].id;
    }
  } catch (error) {
    ElMessage.error("Failed to load lookup data");
    console.error(error);
  }
};

const refreshWorkstationData = async () => {
  if (!selectedWorkstation.value) {
    scheduleItems.value = [];
    activeRecord.value = null;
    completedRecordIndex.value = {};
    return;
  }
  scheduleLoading.value = true;
  try {
    const [scheduleData, activeData, completedData] = await Promise.all([
      getScheduling({ workstation: selectedWorkstation.value }),
      getProductionCounting({
        workstation: selectedWorkstation.value,
        status: "in_progress",
      }),
      getProductionCounting({
        workstation: selectedWorkstation.value,
        status: "completed",
      }),
    ]);
    scheduleItems.value = normalizeListResponse(scheduleData);
    const activeList = normalizeListResponse(activeData);
    activeRecord.value = activeList[0] || null;
    completedRecordIndex.value = buildCompletedIndex(
      normalizeListResponse(completedData)
    );
  } catch (error) {
    ElMessage.error("Failed to load workstation data");
    console.error(error);
  } finally {
    scheduleLoading.value = false;
  }
};

const clockIn = async (task) => {
  if (!selectedOperator.value) {
    ElMessage.warning("Select an operator before clocking in");
    return;
  }
  if (!selectedWorkstation.value) {
    ElMessage.warning("Select a workstation first");
    return;
  }
  if (
    task.productionLineId &&
    selectedWorkstationLine.value &&
    task.productionLineId !== selectedWorkstationLine.value
  ) {
    ElMessage.warning(
      "Selected workstation is not part of the order production line"
    );
    return;
  }
  try {
    await apiStartOperation({
      order: task.order,
      operation: task.operationId,
      component: task.component,
      workstation: selectedWorkstation.value,
      operator: selectedOperator.value,
    });
    ElMessage.success("Clock-in recorded");
    await refreshWorkstationData();
  } catch (error) {
    ElMessage.error("Failed to clock in");
    console.error(error);
  }
};

const openClockOutDialog = (record) => {
  clockOutTarget.value = record;
  clockOutForm.value = {
    produced_quantity: record.produced_quantity || 0,
    scrap_quantity: record.scrap_quantity || 0,
  };
  showClockOutDialog.value = true;
};

const reportMaintenance = () => {
  ElMessage.info("Maintenance request sent to Engineering.");
};

const handleClockOut = async () => {
  if (!clockOutTarget.value) {
    showClockOutDialog.value = false;
    return;
  }
  try {
    await apiStopOperation(
      clockOutTarget.value.id,
      clockOutForm.value.produced_quantity,
      clockOutForm.value.scrap_quantity
    );
    ElMessage.success("Clock-out recorded");
    showClockOutDialog.value = false;
    clockOutTarget.value = null;
    await refreshWorkstationData();
  } catch (error) {
    ElMessage.error("Failed to clock out");
    console.error(error);
  }
};

onMounted(() => {
  loadLookups();
});

watch(selectedWorkstation, () => {
  refreshWorkstationData();
});

watch(selectedProductionLine, () => {
  if (!selectedProductionLine.value) {
    selectedWorkstation.value = null;
    return;
  }
  const first = workstationOptions.value.find(
    (ws) => ws.productionLine === selectedProductionLine.value
  );
  selectedWorkstation.value = first ? first.id : null;
});
</script>

<style scoped>
.operator-panel {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.active-card {
  min-height: 220px;
}

.active-details label {
  font-size: 12px;
  color: #909399;
  display: block;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.active-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}

.queue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.queue-table .order-cell,
.queue-table .operation-cell {
  display: flex;
  flex-direction: column;
}

.order-number {
  font-weight: 600;
}

.secondary-text {
  font-size: 12px;
  color: #909399;
}

.mt-4 {
  margin-top: 16px;
}

.mb-2 {
  margin-bottom: 8px;
}

.instructions-content {
  padding: 10px;
}

.safety-alert {
  margin-top: 16px;
}
</style>
