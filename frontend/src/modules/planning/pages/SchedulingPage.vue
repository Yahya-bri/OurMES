<template>
  <div class="scheduling-page">
    <div class="page-header">
      <h1>Production Scheduling</h1>
      <div class="header-actions">
        <el-button
          type="primary"
          @click="showGenerateDialog = true"
          :icon="Calendar"
        >
          Generate Schedule
        </el-button>
        <el-button
          @click="optimizeSchedule"
          :icon="Connection"
          :loading="optimizing"
        >
          Optimize (Finite Capacity)
        </el-button>
        <el-button
          @click="checkConflicts"
          :icon="Warning"
          :loading="checkingConflicts"
        >
          Check Conflicts
        </el-button>
        <el-switch
          v-model="showMaintenance"
          active-text="Show Maintenance Blocks"
          style="margin-left: 10px"
        />
        <el-dropdown @command="handleExport" style="margin-left: 10px">
          <el-button :icon="Download">
            Export <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="csv">Export as CSV</el-dropdown-item>
              <el-dropdown-item command="excel"
                >Export as Excel</el-dropdown-item
              >
              <el-dropdown-item command="pdf">Export as PDF</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button @click="refreshSchedule" :icon="Refresh">
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Dashboard -->
    <div class="stats-container">
      <el-card class="stat-card stat-total">
        <div class="stat-content">
          <div class="stat-icon">📋</div>
          <div class="stat-info">
            <div class="stat-label">Total Tasks</div>
            <div class="stat-value">{{ stats.total }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card stat-scheduled">
        <div class="stat-content">
          <div class="stat-icon">✓</div>
          <div class="stat-info">
            <div class="stat-label">Scheduled</div>
            <div class="stat-value">{{ stats.scheduled }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card stat-conflicts">
        <div class="stat-content">
          <div class="stat-icon">⚠️</div>
          <div class="stat-info">
            <div class="stat-label">Conflicts</div>
            <div class="stat-value">{{ stats.conflicts }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card stat-utilization">
        <div class="stat-content">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-label">Utilization</div>
            <div class="stat-value">{{ stats.utilization }}%</div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="scheduling-content">
      <!-- Left Sidebar - Orders List -->
      <el-card class="orders-sidebar" shadow="never">
        <template #header>
          <div class="sidebar-header">
            <span class="sidebar-title">Orders</span>
            <el-button text @click="selectAllOrders" size="small">
              {{
                selectedOrders.length === orders.length
                  ? "Deselect All"
                  : "Select All"
              }}
            </el-button>
          </div>
        </template>

        <div class="order-filters">
          <el-input
            v-model="orderSearchText"
            placeholder="Search orders..."
            clearable
            size="small"
            :prefix-icon="Search"
          />
          <el-select
            v-model="orderStatusFilter"
            placeholder="Status"
            clearable
            size="small"
            style="margin-top: 8px; width: 100%"
          >
            <el-option label="All" value="" />
            <el-option label="Pending" value="pending" />
            <el-option label="In Progress" value="in_progress" />
            <el-option label="Completed" value="completed" />
          </el-select>

          <el-select
            v-model="productionLineFilter"
            placeholder="Production Line"
            clearable
            size="small"
            style="margin-top: 8px; width: 100%"
          >
            <el-option label="All Lines" value="" />
            <el-option
              v-for="line in productionLines"
              :key="line.id"
              :label="line.name"
              :value="line.id"
            />
          </el-select>

          <el-date-picker
            v-model="dateRangeFilter"
            type="daterange"
            range-separator="To"
            start-placeholder="Start date"
            end-placeholder="End date"
            size="small"
            style="margin-top: 8px; width: 100%"
            @change="applyDateFilter"
          />
        </div>

        <div class="orders-list" v-loading="loadingOrders">
          <div
            v-for="order in filteredOrders"
            :key="order.id"
            class="order-item"
            :class="{ selected: selectedOrders.includes(order.id) }"
            @click="toggleOrderSelection(order.id)"
          >
            <el-checkbox
              :model-value="selectedOrders.includes(order.id)"
              @change="toggleOrderSelection(order.id)"
              @click.stop
            />
            <div class="order-details">
              <div class="order-number">{{ order.number }}</div>
              <div class="order-name">{{ order.name }}</div>
              <div class="order-meta">
                <el-tag :type="getStatusType(order.state)" size="small">
                  {{ order.state }}
                </el-tag>
                <span class="order-quantity"
                  >Qty: {{ order.planned_quantity }}</span
                >
              </div>
              <div v-if="order.deadline" class="order-deadline">
                <el-icon><Clock /></el-icon>
                {{ formatDate(order.deadline) }}
              </div>
            </div>
            <div class="order-actions">
              <el-tooltip
                v-if="!order.technology"
                content="Assign a routing to this order first"
                placement="top"
              >
                <span>
                  <el-button
                    text
                    type="primary"
                    size="small"
                    :disabled="!order.technology"
                    @click.stop="generateForOrder(order)"
                    :loading="generatingOrder === order.id"
                  >
                    Generate
                  </el-button>
                </span>
              </el-tooltip>
              <el-button
                v-else
                text
                type="primary"
                size="small"
                @click.stop="generateForOrder(order)"
                :loading="generatingOrder === order.id"
              >
                Generate
              </el-button>
              <el-dropdown
                @command="handleOrderAction($event, order.id)"
                trigger="click"
              >
                <el-button text size="small" :icon="MoreFilled" />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="view"
                      >View Details</el-dropdown-item
                    >
                    <el-dropdown-item command="clear"
                      >Clear Schedule</el-dropdown-item
                    >
                    <el-dropdown-item command="lock"
                      >Lock Tasks</el-dropdown-item
                    >
                    <el-dropdown-item command="unlock"
                      >Unlock Tasks</el-dropdown-item
                    >
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <el-empty
            v-if="filteredOrders.length === 0"
            description="No orders found"
            :image-size="100"
          />
        </div>

        <div class="sidebar-footer">
          <el-statistic
            title="Selected Orders"
            :value="selectedOrders.length"
          />
          <el-statistic title="Total Tasks" :value="ganttTasks.length" />
        </div>
      </el-card>

      <!-- Main Content - Gantt Chart -->
      <div class="gantt-section">
        <el-card shadow="never" :body-style="{ padding: 0, height: '100%' }">
          <div class="gantt-controls">
            <div class="gantt-controls-left">
              <el-radio-group v-model="viewMode" size="small">
                <el-radio-button label="gantt">Gantt Chart</el-radio-button>
                <el-radio-button label="list">List View</el-radio-button>
                <el-radio-button label="calendar">Calendar</el-radio-button>
              </el-radio-group>
            </div>
            <div class="gantt-controls-right">
              <el-select
                v-model="workstationFilter"
                placeholder="Filter by Workstation"
                clearable
                size="small"
                style="width: 200px"
              >
                <el-option label="All Workstations" value="" />
                <el-option
                  v-for="ws in workstations"
                  :key="ws.id"
                  :label="ws.name"
                  :value="ws.id"
                />
              </el-select>

              <el-button
                v-if="selectedTasks.length > 0"
                size="small"
                type="primary"
                @click="showBulkEditDialog = true"
                style="margin-left: 10px"
              >
                Bulk Edit ({{ selectedTasks.length }})
              </el-button>
            </div>
          </div>

          <div class="gantt-wrapper" v-loading="loadingSchedule">
            <!-- Gantt Chart View -->
            <GanttChart
              v-if="viewMode === 'gantt' && ganttTasks.length > 0"
              :tasks="filteredTasks"
              :orders="orders"
              @task-updated="handleTaskUpdate"
              @task-selected="handleTaskSelected"
              @tasks-selected="handleTasksSelected"
            />

            <!-- List View -->
            <div
              v-else-if="viewMode === 'list' && ganttTasks.length > 0"
              class="list-view"
            >
              <el-table
                :data="filteredTasks"
                style="width: 100%"
                @selection-change="handleTasksSelected"
              >
                <el-table-column type="selection" width="55" />
                <el-table-column prop="orderNumber" label="Order" width="120" />
                <el-table-column
                  prop="name"
                  label="Operation"
                  min-width="200"
                />
                <el-table-column
                  prop="sequenceIndex"
                  label="Sequence"
                  width="100"
                  align="center"
                />
                <el-table-column label="Start" width="160">
                  <template #default="scope">
                    {{ formatDateTime(scope.row.start) }}
                  </template>
                </el-table-column>
                <el-table-column label="End" width="160">
                  <template #default="scope">
                    {{ formatDateTime(scope.row.end) }}
                  </template>
                </el-table-column>
                <el-table-column label="Duration" width="100">
                  <template #default="scope">
                    {{ formatDuration(scope.row.duration) }}
                  </template>
                </el-table-column>
                <el-table-column label="Status" width="100">
                  <template #default="scope">
                    <el-tag v-if="scope.row.locked" type="warning" size="small"
                      >Locked</el-tag
                    >
                    <el-tag v-else type="success" size="small">Active</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Actions" width="150" fixed="right">
                  <template #default="scope">
                    <el-button
                      size="small"
                      @click="handleTaskSelected(scope.row.id)"
                    >
                      Edit
                    </el-button>
                    <el-button
                      size="small"
                      type="danger"
                      @click="deleteTaskById(scope.row.id)"
                    >
                      Delete
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- Calendar View -->
            <div v-else-if="viewMode === 'calendar'" class="calendar-view">
              <el-calendar v-model="calendarDate">
                <template #date-cell="{ data }">
                  <div class="calendar-day">
                    <div class="day-number">
                      {{ data.day.split("-").slice(2) }}
                    </div>
                    <div class="day-tasks">
                      <el-tag
                        v-for="task in getTasksForDate(data.day)"
                        :key="task.id"
                        size="small"
                        :type="task.locked ? 'warning' : 'primary'"
                        style="margin: 2px; font-size: 10px"
                        @click="handleTaskSelected(task.id)"
                      >
                        {{ task.shortName }}
                      </el-tag>
                    </div>
                  </div>
                </template>
              </el-calendar>
            </div>

            <el-empty
              v-else
              description="No schedule data. Select orders and generate schedule."
              :image-size="200"
            />
          </div>
        </el-card>
      </div>
    </div>

    <!-- Task Details Panel -->
    <el-drawer
      v-model="showTaskDetails"
      title="Task Details"
      direction="rtl"
      size="400px"
    >
      <div v-if="selectedTaskData" class="task-details-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Order">
            <el-tag>{{ selectedTaskData.orderNumber }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Operation">
            {{ selectedTaskData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="Sequence">
            {{ selectedTaskData.sequenceIndex }}
          </el-descriptions-item>
          <el-descriptions-item label="Planned Start">
            {{ formatDateTime(selectedTaskData.start) }}
          </el-descriptions-item>
          <el-descriptions-item label="Planned End">
            {{ formatDateTime(selectedTaskData.end) }}
          </el-descriptions-item>
          <el-descriptions-item label="Duration">
            {{ formatDuration(selectedTaskData.duration) }}
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag v-if="selectedTaskData.locked" type="warning"
              >Locked</el-tag
            >
            <el-tag v-else type="success">Editable</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <el-form label-position="top">
          <el-form-item label="Planned Start">
            <el-date-picker
              v-model="editTaskForm.start"
              type="datetime"
              style="width: 100%"
              :disabled="selectedTaskData.locked"
            />
          </el-form-item>
          <el-form-item label="Planned End">
            <el-date-picker
              v-model="editTaskForm.end"
              type="datetime"
              style="width: 100%"
              :disabled="selectedTaskData.locked"
            />
          </el-form-item>
          <el-form-item label="Lock Task">
            <el-switch v-model="editTaskForm.locked" />
          </el-form-item>
          <el-form-item label="Notes">
            <el-input
              v-model="editTaskForm.description"
              type="textarea"
              :rows="4"
              placeholder="Add notes or description..."
            />
          </el-form-item>
        </el-form>

        <div class="task-actions">
          <el-button
            type="primary"
            @click="saveTaskChanges"
            style="width: 100%"
          >
            Save Changes
          </el-button>
          <el-button
            type="danger"
            @click="deleteTask"
            style="width: 100%; margin-top: 8px"
          >
            Delete Task
          </el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Generate Schedule Dialog -->
    <el-dialog
      v-model="showGenerateDialog"
      title="Generate Production Schedule"
      width="600px"
    >
      <el-form label-width="140px">
        <el-form-item label="Orders">
          <el-select
            v-model="generateForm.orderIds"
            multiple
            filterable
            placeholder="Select one or more orders"
            style="width: 100%"
          >
            <el-option
              v-for="order in orders"
              :key="order.id"
              :label="`${order.number} - ${order.name}`"
              :value="order.id"
            />
          </el-select>
          <div style="margin-top: 8px">
            <el-button
              text
              size="small"
              @click="generateForm.orderIds = selectedOrders"
            >
              Use Selected ({{ selectedOrders.length }})
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="Start Date">
          <el-date-picker
            v-model="generateForm.startDate"
            type="datetime"
            style="width: 100%"
            placeholder="Leave empty for now"
          />
        </el-form-item>

        <el-form-item label="Clear Existing">
          <el-switch v-model="generateForm.clearExisting" />
          <div class="form-help-text">
            Remove existing schedule items for selected orders before generating
          </div>
        </el-form-item>

        <el-form-item label="Algorithm">
          <el-radio-group v-model="generateForm.algorithm">
            <el-radio label="sequential">Sequential (Order by Order)</el-radio>
            <el-radio label="parallel">Parallel (Optimize Resources)</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showGenerateDialog = false">Cancel</el-button>
        <el-button
          type="primary"
          @click="handleGenerateMultiSchedule"
          :loading="generating"
        >
          Generate Schedule
        </el-button>
      </template>
    </el-dialog>

    <!-- Bulk Edit Dialog -->
    <el-dialog
      v-model="showBulkEditDialog"
      title="Bulk Edit Tasks"
      width="500px"
    >
      <el-form label-width="140px">
        <el-form-item label="Shift Start By">
          <el-input-number
            v-model="bulkEditForm.shiftHours"
            :min="-240"
            :max="240"
            style="width: 100%"
          />
          <div class="form-help-text">
            Hours to shift all selected tasks (negative for earlier)
          </div>
        </el-form-item>

        <el-form-item label="Lock Tasks">
          <el-switch v-model="bulkEditForm.locked" />
        </el-form-item>

        <el-form-item label="Add Note">
          <el-input
            v-model="bulkEditForm.note"
            type="textarea"
            :rows="3"
            placeholder="Add a note to all selected tasks..."
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showBulkEditDialog = false">Cancel</el-button>
        <el-button
          type="primary"
          @click="applyBulkEdit"
          :loading="applyingBulk"
        >
          Apply to {{ selectedTasks.length }} Tasks
        </el-button>
      </template>
    </el-dialog>

    <!-- Conflicts Dialog -->
    <el-dialog
      v-model="showConflictsDialog"
      title="Schedule Conflicts"
      width="700px"
    >
      <el-alert
        v-if="conflicts.length === 0"
        title="No conflicts found"
        type="success"
        :closable="false"
        show-icon
      />

      <div v-else>
        <el-alert
          title="Conflicts Detected"
          :description="`Found ${conflicts.length} scheduling conflicts that need attention.`"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 15px"
        />

        <div class="conflicts-list">
          <el-card
            v-for="(conflict, idx) in conflicts"
            :key="idx"
            shadow="hover"
            style="margin-bottom: 10px"
          >
            <div class="conflict-item">
              <div class="conflict-header">
                <el-tag type="danger" size="small"
                  >Conflict #{{ idx + 1 }}</el-tag
                >
                <span class="conflict-type">{{
                  formatConflictType(conflict.type)
                }}</span>
              </div>
              <div class="conflict-details">
                <div>
                  <strong>Task 1:</strong>
                  {{ conflict.task1.operation }} (Order:
                  {{ conflict.task1.order }})
                </div>
                <div>
                  <strong>Time:</strong>
                  {{ formatDateTime(conflict.task1.start) }} -
                  {{ formatDateTime(conflict.task1.end) }}
                </div>
                <div>
                  <strong>Task 2:</strong>
                  {{ conflict.task2.operation }} (Order:
                  {{ conflict.task2.order }})
                </div>
                <div>
                  <strong>Time:</strong>
                  {{ formatDateTime(conflict.task2.start) }} -
                  {{ formatDateTime(conflict.task2.end) }}
                </div>
                <div>
                  <strong>Overlap:</strong>
                  {{ formatDateTime(conflict.overlap_start) }} -
                  {{ formatDateTime(conflict.overlap_end) }}
                </div>
                <div v-if="conflict.resource">
                  <strong>Resource:</strong> {{ conflict.resource }}
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <template #footer>
        <el-button @click="showConflictsDialog = false">Close</el-button>
        <el-button
          v-if="conflicts.length > 0"
          type="primary"
          @click="autoResolveConflicts"
        >
          Auto Resolve
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Calendar,
  Connection,
  Refresh,
  Search,
  MoreFilled,
  Download,
  ArrowDown,
  Warning,
  Clock,
} from "@element-plus/icons-vue";
import GanttChart from "@/components/GanttChart.vue";
import {
  getScheduling,
  generateSchedule,
  generateMultiOrderSchedule,
  updateScheduleItem,
  bulkUpdateSchedule,
  deleteScheduleItem,
  deleteScheduleByOrder,
  optimizeSchedule as optimizeScheduleAPI,
  checkConflicts as checkConflictsAPI,
} from "../services/schedulingService";
import { getOrders } from "@/modules/orders/services/ordersService";
import {
  getProductionLines,
  getWorkstations,
} from "@/modules/basic-data/services/basicDataService";

// Data refs
const orders = ref([]);
const scheduleItems = ref([]);
const productionLines = ref([]);
const workstations = ref([]);
const selectedOrders = ref([]);
const selectedTask = ref(null);
const selectedTaskData = ref(null);
const selectedTasks = ref([]);
const conflicts = ref([]);
const stats = ref({
  total: 0,
  scheduled: 0,
  conflicts: 0,
  utilization: 0,
});

// UI state
const loadingOrders = ref(false);
const loadingSchedule = ref(false);
const generating = ref(false);
const generatingOrder = ref(null);
const optimizing = ref(false);
const checkingConflicts = ref(false);
const applyingBulk = ref(false);
const showGenerateDialog = ref(false);
const showMaintenance = ref(true);
const showTaskDetails = ref(false);
const showBulkEditDialog = ref(false);
const showConflictsDialog = ref(false);
const viewMode = ref("gantt");
const calendarDate = ref(new Date());

// Filters
const orderSearchText = ref("");
const orderStatusFilter = ref("");
const productionLineFilter = ref("");
const workstationFilter = ref("");
const dateRangeFilter = ref(null);

// Forms
const generateForm = ref({
  orderIds: [],
  startDate: null,
  clearExisting: true,
  algorithm: "sequential",
});

const editTaskForm = ref({
  start: null,
  end: null,
  locked: false,
  description: "",
});

const bulkEditForm = ref({
  shiftHours: 0,
  locked: false,
  note: "",
});

// Computed
const filteredOrders = computed(() => {
  let filtered = orders.value;

  // Search filter
  if (orderSearchText.value) {
    const search = orderSearchText.value.toLowerCase();
    filtered = filtered.filter(
      (order) =>
        order.number.toLowerCase().includes(search) ||
        order.name.toLowerCase().includes(search)
    );
  }

  // Status filter
  if (orderStatusFilter.value) {
    filtered = filtered.filter(
      (order) => order.state === orderStatusFilter.value
    );
  }

  // Production line filter
  if (productionLineFilter.value) {
    filtered = filtered.filter(
      (order) => order.production_line === productionLineFilter.value
    );
  }

  // Date range filter
  if (
    dateRangeFilter.value &&
    dateRangeFilter.value[0] &&
    dateRangeFilter.value[1]
  ) {
    const [start, end] = dateRangeFilter.value;
    filtered = filtered.filter((order) => {
      if (!order.deadline) return true;
      const deadline = new Date(order.deadline);
      return deadline >= start && deadline <= end;
    });
  }

  return filtered;
});

const ganttTasks = computed(() => {
  return scheduleItems.value.map((item) => ({
    id: item.id,
    name: item.component_name || `Operation ${item.component}`,
    shortName: item.component_name?.substring(0, 15) || `Op ${item.component}`,
    start: item.planned_start,
    end: item.planned_end,
    duration: item.duration_seconds,
    orderId: item.order,
    orderNumber: item.order_number,
    sequenceIndex: item.sequence_index,
    locked: item.locked || false,
    description: item.description || "",
    workstation: item.workstation,
  }));
});

const filteredTasks = computed(() => {
  let filtered = ganttTasks.value;

  // Workstation filter
  if (workstationFilter.value) {
    filtered = filtered.filter(
      (task) => task.workstation === workstationFilter.value
    );
  }

  return filtered;
});

// Methods
const calculateStats = () => {
  const total = ganttTasks.value.length;
  const scheduled = ganttTasks.value.filter((t) => t.start && t.end).length;
  const conflictsCount = conflicts.value.length;

  // Simple utilization calculation (scheduled tasks / total)
  const utilization = total > 0 ? Math.round((scheduled / total) * 100) : 0;

  stats.value = {
    total,
    scheduled,
    conflicts: conflictsCount,
    utilization,
  };
};

const loadOrders = async () => {
  loadingOrders.value = true;
  try {
    const data = await getOrders({});
    orders.value = data.results || data;
  } catch (error) {
    ElMessage.error("Failed to load orders");
    console.error(error);
  } finally {
    loadingOrders.value = false;
  }
};

const loadProductionLines = async () => {
  try {
    const data = await getProductionLines();
    productionLines.value = data.results || data;
  } catch (error) {
    console.error("Failed to load production lines:", error);
  }
};

const loadWorkstations = async () => {
  try {
    const data = await getWorkstations();
    workstations.value = data.results || data;
  } catch (error) {
    console.error("Failed to load workstations:", error);
  }
};

const loadSchedule = async () => {
  loadingSchedule.value = true;
  try {
    const params = {};
    if (selectedOrders.value.length > 0) {
      params.order__in = selectedOrders.value.join(",");
    }
    const data = await getScheduling(params);
    scheduleItems.value = data.results || data;
    calculateStats();
  } catch (error) {
    ElMessage.error("Failed to load schedule");
    console.error(error);
  } finally {
    loadingSchedule.value = false;
  }
};

const refreshSchedule = () => {
  loadSchedule();
};

const applyDateFilter = () => {
  // Trigger filtered orders recomputation
  orderSearchText.value = orderSearchText.value;
};

const toggleOrderSelection = (orderId) => {
  const index = selectedOrders.value.indexOf(orderId);
  if (index > -1) {
    selectedOrders.value.splice(index, 1);
  } else {
    selectedOrders.value.push(orderId);
  }
};

const selectAllOrders = () => {
  if (selectedOrders.value.length === orders.value.length) {
    selectedOrders.value = [];
  } else {
    selectedOrders.value = orders.value.map((o) => o.id);
  }
};

const generateForOrder = async (order) => {
  if (!order.technology) {
    ElMessage.warning("Order has no routing assigned");
    return;
  }
  generatingOrder.value = order.id;
  try {
    await generateSchedule(order.id);
    ElMessage.success("Schedule generated successfully");
    loadSchedule();
  } catch (error) {
    ElMessage.error("Failed to generate schedule");
    console.error(error);
  } finally {
    generatingOrder.value = null;
  }
};

const handleGenerateMultiSchedule = async () => {
  if (generateForm.value.orderIds.length === 0) {
    ElMessage.warning("Please select at least one order");
    return;
  }

  generating.value = true;
  try {
    // Clear existing if requested
    if (generateForm.value.clearExisting) {
      for (const orderId of generateForm.value.orderIds) {
        try {
          await deleteScheduleByOrder(orderId);
        } catch (error) {
          console.warn(`Failed to clear schedule for order ${orderId}:`, error);
        }
      }
    }

    // Generate new schedule
    const startDate = generateForm.value.startDate?.toISOString() || null;
    await generateMultiOrderSchedule(generateForm.value.orderIds, startDate);

    ElMessage.success("Schedule generated successfully");
    showGenerateDialog.value = false;
    loadSchedule();
  } catch (error) {
    ElMessage.error("Failed to generate schedule");
    console.error(error);
  } finally {
    generating.value = false;
  }
};

const handleTaskUpdate = async (update) => {
  try {
    await updateScheduleItem(update.id, {
      planned_start: update.start,
      planned_end: update.end,
    });
    ElMessage.success("Task updated");
    loadSchedule();
  } catch (error) {
    ElMessage.error("Failed to update task");
    console.error(error);
  }
};

const handleTaskSelected = (taskId) => {
  selectedTask.value = taskId;
  if (taskId) {
    const task = ganttTasks.value.find((t) => t.id === taskId);
    if (task) {
      selectedTaskData.value = task;
      editTaskForm.value = {
        start: new Date(task.start),
        end: new Date(task.end),
        locked: task.locked,
        description: task.description,
      };
      showTaskDetails.value = true;
    }
  } else {
    showTaskDetails.value = false;
  }
};

const handleTasksSelected = (tasks) => {
  selectedTasks.value = Array.isArray(tasks) ? tasks : [];
};

const saveTaskChanges = async () => {
  try {
    await updateScheduleItem(selectedTaskData.value.id, {
      planned_start: editTaskForm.value.start.toISOString(),
      planned_end: editTaskForm.value.end.toISOString(),
      locked: editTaskForm.value.locked,
      description: editTaskForm.value.description,
    });
    ElMessage.success("Task updated successfully");
    loadSchedule();
    showTaskDetails.value = false;
  } catch (error) {
    ElMessage.error("Failed to update task");
    console.error(error);
  }
};

const deleteTask = async () => {
  try {
    await ElMessageBox.confirm(
      "Are you sure you want to delete this task?",
      "Warning",
      {
        confirmButtonText: "Delete",
        cancelButtonText: "Cancel",
        type: "warning",
      }
    );

    await deleteScheduleItem(selectedTaskData.value.id);
    ElMessage.success("Task deleted");
    loadSchedule();
    showTaskDetails.value = false;
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("Failed to delete task");
      console.error(error);
    }
  }
};

const deleteTaskById = async (taskId) => {
  try {
    await ElMessageBox.confirm(
      "Are you sure you want to delete this task?",
      "Warning",
      { type: "warning" }
    );

    await deleteScheduleItem(taskId);
    ElMessage.success("Task deleted");
    loadSchedule();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("Failed to delete task");
    }
  }
};

const handleOrderAction = async (command, orderId) => {
  switch (command) {
    case "view":
      ElMessage.info("Navigate to order details");
      break;
    case "clear":
      try {
        await ElMessageBox.confirm(
          "Clear all schedule items for this order?",
          "Warning",
          { type: "warning" }
        );
        await deleteScheduleByOrder(orderId);
        ElMessage.success("Schedule cleared");
        loadSchedule();
      } catch (error) {
        if (error !== "cancel") {
          ElMessage.error("Failed to clear schedule");
        }
      }
      break;
    case "lock":
      await lockOrderTasks(orderId, true);
      break;
    case "unlock":
      await lockOrderTasks(orderId, false);
      break;
  }
};

const lockOrderTasks = async (orderId, locked) => {
  try {
    const tasksToUpdate = scheduleItems.value
      .filter((item) => item.order === orderId)
      .map((item) => ({
        id: item.id,
        locked: locked,
      }));

    await bulkUpdateSchedule(tasksToUpdate);
    ElMessage.success(`Tasks ${locked ? "locked" : "unlocked"}`);
    loadSchedule();
  } catch (error) {
    ElMessage.error(`Failed to ${locked ? "lock" : "unlock"} tasks`);
  }
};

const applyBulkEdit = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning("No tasks selected");
    return;
  }

  applyingBulk.value = true;
  try {
    const updates = selectedTasks.value.map((task) => {
      const update = { id: task.id };

      // Shift dates if specified
      if (bulkEditForm.value.shiftHours !== 0) {
        const shiftMs = bulkEditForm.value.shiftHours * 3600 * 1000;
        const newStart = new Date(new Date(task.start).getTime() + shiftMs);
        const newEnd = new Date(new Date(task.end).getTime() + shiftMs);
        update.planned_start = newStart.toISOString();
        update.planned_end = newEnd.toISOString();
      }

      // Update lock status
      update.locked = bulkEditForm.value.locked;

      // Add note
      if (bulkEditForm.value.note) {
        update.description = task.description
          ? `${task.description}\n${bulkEditForm.value.note}`
          : bulkEditForm.value.note;
      }

      return update;
    });

    await bulkUpdateSchedule(updates);
    ElMessage.success(`${selectedTasks.value.length} tasks updated`);
    showBulkEditDialog.value = false;
    bulkEditForm.value = { shiftHours: 0, locked: false, note: "" };
    selectedTasks.value = [];
    loadSchedule();
  } catch (error) {
    ElMessage.error("Failed to update tasks");
    console.error(error);
  } finally {
    applyingBulk.value = false;
  }
};

const checkConflicts = async () => {
  if (selectedOrders.value.length === 0) {
    ElMessage.warning("Please select orders to check for conflicts");
    return;
  }

  checkingConflicts.value = true;
  try {
    // Gather all scheduled tasks for selected orders
    const tasksToCheck = scheduledTasks.value
      .filter((task) => selectedOrders.value.includes(task.order))
      .map((task) => ({
        id: task.id,
        order: task.order,
        operation: task.operation_name,
        start: task.start_datetime,
        end: task.end_datetime,
        workstation: task.workstation,
        production_line: task.production_line,
      }));

    if (tasksToCheck.length === 0) {
      ElMessage.warning("No scheduled tasks found for selected orders");
      return;
    }

    const response = await checkConflictsAPI(tasksToCheck);
    conflicts.value = response.conflicts || [];
    calculateStats();
    showConflictsDialog.value = true;

    if (conflicts.value.length === 0) {
      ElMessage.success("No conflicts detected");
    } else {
      ElMessage.warning(`Found ${conflicts.value.length} conflicts`);
    }
  } catch (error) {
    ElMessage.error("Failed to check conflicts");
    console.error(error);
  } finally {
    checkingConflicts.value = false;
  }
};

const autoResolveConflicts = async () => {
  try {
    await ElMessageBox.confirm(
      "Automatically adjust task times to resolve conflicts?",
      "Auto Resolve",
      { type: "info" }
    );

    // Simple conflict resolution: shift conflicting tasks
    for (const conflict of conflicts.value) {
      // Implement basic resolution logic
      // This would need backend support for more sophisticated resolution
      ElMessage.info("Auto-resolve functionality requires backend support");
    }

    showConflictsDialog.value = false;
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("Failed to resolve conflicts");
    }
  }
};

const optimizeSchedule = async () => {
  if (selectedOrders.value.length === 0) {
    ElMessage.warning("Please select orders to optimize");
    return;
  }

  optimizing.value = true;
  try {
    await optimizeScheduleAPI(selectedOrders.value, "earliest");
    ElMessage.success("Schedule optimized");
    loadSchedule();
  } catch (error) {
    ElMessage.error("Failed to optimize schedule");
    console.error(error);
  } finally {
    optimizing.value = false;
  }
};

const handleExport = (format) => {
  if (ganttTasks.value.length === 0) {
    ElMessage.warning("No data to export");
    return;
  }

  switch (format) {
    case "csv":
      exportToCSV();
      break;
    case "excel":
      ElMessage.info("Excel export coming soon");
      break;
    case "pdf":
      ElMessage.info("PDF export coming soon");
      break;
  }
};

const exportToCSV = () => {
  const headers = [
    "Order",
    "Operation",
    "Sequence",
    "Start",
    "End",
    "Duration (s)",
    "Locked",
    "Description",
  ];
  const rows = ganttTasks.value.map((task) => [
    task.orderNumber,
    task.name,
    task.sequenceIndex,
    task.start,
    task.end,
    task.duration,
    task.locked ? "Yes" : "No",
    task.description || "",
  ]);

  const csvContent = [
    headers.join(","),
    ...rows.map((row) => row.map((cell) => `"${cell}"`).join(",")),
  ].join("\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `schedule_${new Date().toISOString().split("T")[0]}.csv`;
  link.click();

  ElMessage.success("CSV exported successfully");
};

const getTasksForDate = (dateStr) => {
  const date = new Date(dateStr);
  return ganttTasks.value.filter((task) => {
    const start = new Date(task.start);
    const end = new Date(task.end);
    return date >= start && date <= end;
  });
};

const getStatusType = (state) => {
  const statusMap = {
    pending: "",
    in_progress: "warning",
    completed: "success",
    cancelled: "danger",
  };
  return statusMap[state] || "info";
};

const formatDateTime = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatConflictType = (type) => {
  const typeMap = {
    workstation_conflict: "Workstation Conflict",
    production_line_conflict: "Production Line Conflict",
    time_overlap: "Time Overlap",
  };
  return typeMap[type] || type;
};

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

const formatDuration = (seconds) => {
  if (!seconds) return "0m";
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
};

// Watch for order selection changes
watch(
  selectedOrders,
  () => {
    loadSchedule();
  },
  { deep: true }
);

// Lifecycle
onMounted(() => {
  loadOrders();
  loadProductionLines();
  loadWorkstations();
  loadSchedule();
});
</script>

<style scoped>
.scheduling-page {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* Stats Dashboard */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  font-size: 28px;
  line-height: 1;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-total {
  border-left: 4px solid #409eff;
}

.stat-scheduled {
  border-left: 4px solid #67c23a;
}

.stat-conflicts {
  border-left: 4px solid #f56c6c;
}

.stat-utilization {
  border-left: 4px solid #e6a23c;
}

.scheduling-content {
  display: flex;
  gap: 20px;
  flex: 1;
  overflow: hidden;
}

.orders-sidebar {
  width: 350px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  max-height: 100%;
}

.orders-sidebar :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-title {
  font-weight: 600;
  font-size: 16px;
}

.order-filters {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
}

.orders-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.order-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.order-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.order-item.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.order-details {
  flex: 1;
  margin-left: 12px;
  min-width: 0;
}

.order-number {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.order-name {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-quantity {
  font-size: 12px;
  color: #909399;
}

.order-deadline {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #f56c6c;
  margin-top: 4px;
}

.order-actions {
  display: flex;
  gap: 4px;
  margin-left: 8px;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: space-around;
  background: #fafafa;
}

.gantt-section {
  flex: 1;
  overflow: hidden;
}

.gantt-section :deep(.el-card__body) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.gantt-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  background: white;
}

.gantt-controls-left,
.gantt-controls-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.gantt-wrapper {
  flex: 1;
  overflow: hidden;
}

.list-view {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.calendar-view {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.calendar-day {
  min-height: 80px;
  padding: 4px;
}

.day-number {
  font-weight: bold;
  margin-bottom: 4px;
}

.day-tasks {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.task-details-content {
  padding: 0 4px;
}

.task-actions {
  margin-top: 20px;
}

.form-help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.conflicts-list {
  max-height: 400px;
  overflow-y: auto;
}

.conflict-item {
  padding: 4px;
}

.conflict-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.conflict-type {
  font-weight: 600;
  color: #303133;
}

.conflict-details {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.conflict-details > div {
  margin-bottom: 4px;
}

/* Scrollbar styling */
.orders-list::-webkit-scrollbar,
.conflicts-list::-webkit-scrollbar {
  width: 6px;
}

.orders-list::-webkit-scrollbar-track,
.conflicts-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.orders-list::-webkit-scrollbar-thumb,
.conflicts-list::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.orders-list::-webkit-scrollbar-thumb:hover,
.conflicts-list::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }

  .orders-sidebar {
    width: 300px;
  }
}

@media (max-width: 768px) {
  .stats-container {
    grid-template-columns: 1fr;
  }

  .scheduling-content {
    flex-direction: column;
  }

  .orders-sidebar {
    width: 100%;
    max-height: 300px;
  }

  .gantt-controls {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
