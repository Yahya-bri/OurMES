<template>
  <div class="gantt-container">
    <div class="gantt-toolbar">
      <el-button-group>
        <el-button 
          :type="viewMode === 'Day' ? 'primary' : 'default'" 
          @click="changeViewMode('Day')"
          size="small"
        >
          Day
        </el-button>
        <el-button 
          :type="viewMode === 'Week' ? 'primary' : 'default'" 
          @click="changeViewMode('Week')"
          size="small"
        >
          Week
        </el-button>
        <el-button 
          :type="viewMode === 'Month' ? 'primary' : 'default'" 
          @click="changeViewMode('Month')"
          size="small"
        >
          Month
        </el-button>
      </el-button-group>
      
      <el-button @click="zoomIn" size="small" style="margin-left: 10px;">
        <el-icon><ZoomIn /></el-icon>
      </el-button>
      <el-button @click="zoomOut" size="small">
        <el-icon><ZoomOut /></el-icon>
      </el-button>
      
      <el-button @click="fitToScreen" size="small" style="margin-left: 10px;">
        Fit to Screen
      </el-button>
    </div>
    
    <div ref="ganttContainer" class="gantt-chart-wrapper">
      <div class="gantt-grid">
        <!-- Task List Column -->
        <div class="gantt-list">
          <div class="gantt-list-header">
            <div class="list-column order-col">Order</div>
            <div class="list-column operation-col">Operation</div>
            <div class="list-column duration-col">Duration</div>
          </div>
          <div class="gantt-list-body">
            <div 
              v-for="task in tasks" 
              :key="task.id" 
              class="gantt-list-row"
              :class="{ 'selected': task.id === selectedTask, 'locked': task.locked }"
              @click="selectTask(task.id)"
            >
              <div class="list-column order-col" :title="task.orderNumber">
                {{ task.orderNumber }}
              </div>
              <div class="list-column operation-col" :title="task.name">
                {{ task.name }}
              </div>
              <div class="list-column duration-col">
                {{ formatDuration(task.duration) }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- Timeline Chart -->
        <div class="gantt-timeline" ref="timeline">
          <div class="gantt-timeline-header">
            <svg :width="timelineWidth" :height="headerHeight">
              <!-- Time scale rendering -->
              <g v-for="(period, idx) in timePeriods" :key="idx">
                <line 
                  :x1="period.x" 
                  :y1="0" 
                  :x2="period.x" 
                  :y2="headerHeight" 
                  stroke="#dcdfe6" 
                  stroke-width="1"
                />
                <text 
                  :x="period.x + period.width / 2" 
                  :y="headerHeight / 2" 
                  text-anchor="middle" 
                  dominant-baseline="middle"
                  font-size="12"
                  fill="#606266"
                >
                  {{ period.label }}
                </text>
              </g>
            </svg>
          </div>
          
          <div class="gantt-timeline-body" @scroll="handleScroll">
            <svg :width="timelineWidth" :height="timelineHeight" @click="deselectTask">
              <!-- Grid lines -->
              <g class="grid-lines">
                <line 
                  v-for="(period, idx) in timePeriods" 
                  :key="'grid-' + idx"
                  :x1="period.x" 
                  :y1="0" 
                  :x2="period.x" 
                  :y2="timelineHeight" 
                  stroke="#f0f0f0" 
                  stroke-width="1"
                />
                <line 
                  v-for="(task, idx) in tasks" 
                  :key="'row-' + idx"
                  :x1="0" 
                  :y1="(idx + 1) * rowHeight" 
                  :x2="timelineWidth" 
                  :y2="(idx + 1) * rowHeight" 
                  stroke="#f5f7fa" 
                  stroke-width="1"
                />
              </g>
              
              <!-- Today line -->
              <line 
                v-if="todayX >= 0 && todayX <= timelineWidth"
                :x1="todayX" 
                :y1="0" 
                :x2="todayX" 
                :y2="timelineHeight" 
                stroke="#f56c6c" 
                stroke-width="2" 
                stroke-dasharray="5,5"
              />
              
              <!-- Task bars -->
              <g v-for="(task, idx) in tasks" :key="'task-' + task.id">
                <rect 
                  :x="getTaskX(task)" 
                  :y="idx * rowHeight + 8" 
                  :width="getTaskWidth(task)" 
                  :height="rowHeight - 16"
                  :fill="getTaskColor(task)"
                  :stroke="task.id === selectedTask ? '#409eff' : '#dcdfe6'"
                  :stroke-width="task.id === selectedTask ? 2 : 1"
                  :class="{ 'task-bar': true, 'locked': task.locked, 'draggable': !task.locked }"
                  @mousedown="startDrag($event, task, idx)"
                  @click.stop="selectTask(task.id)"
                  rx="4"
                  style="cursor: pointer;"
                />
                
                <!-- Task label -->
                <text 
                  :x="getTaskX(task) + 8" 
                  :y="idx * rowHeight + rowHeight / 2" 
                  fill="white"
                  font-size="12"
                  font-weight="500"
                  dominant-baseline="middle"
                  pointer-events="none"
                >
                  {{ task.shortName }}
                </text>
                
                <!-- Resize handles -->
                <rect 
                  v-if="task.id === selectedTask && !task.locked"
                  :x="getTaskX(task) - 4" 
                  :y="idx * rowHeight + 8" 
                  width="8" 
                  :height="rowHeight - 16"
                  fill="#409eff"
                  style="cursor: ew-resize;"
                  @mousedown.stop="startResize($event, task, 'start')"
                />
                <rect 
                  v-if="task.id === selectedTask && !task.locked"
                  :x="getTaskX(task) + getTaskWidth(task) - 4" 
                  :y="idx * rowHeight + 8" 
                  width="8" 
                  :height="rowHeight - 16"
                  fill="#409eff"
                  style="cursor: ew-resize;"
                  @mousedown.stop="startResize($event, task, 'end')"
                />
              </g>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { format, addDays, addHours, differenceInMilliseconds, startOfDay, endOfDay } from 'date-fns';
import { ZoomIn, ZoomOut } from '@element-plus/icons-vue';

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  },
  orders: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['task-updated', 'task-selected']);

// Gantt settings
const viewMode = ref('Day');
const rowHeight = 50;
const headerHeight = 40;
const pixelsPerHour = ref(40);
const ganttContainer = ref(null);
const timeline = ref(null);
const selectedTask = ref(null);

// Drag state
const dragging = ref(false);
const resizing = ref(false);
const resizeMode = ref(null); // 'start' or 'end'
const draggedTask = ref(null);
const dragStartX = ref(0);
const dragStartTime = ref(null);

// Computed properties
const timelineHeight = computed(() => props.tasks.length * rowHeight);

const timeRange = computed(() => {
  if (props.tasks.length === 0) {
    const now = new Date();
    return {
      start: startOfDay(now),
      end: endOfDay(addDays(now, 7))
    };
  }
  
  const starts = props.tasks.map(t => new Date(t.start));
  const ends = props.tasks.map(t => new Date(t.end));
  
  const minStart = new Date(Math.min(...starts));
  const maxEnd = new Date(Math.max(...ends));
  
  // Add padding
  return {
    start: addDays(startOfDay(minStart), -1),
    end: addDays(endOfDay(maxEnd), 1)
  };
});

const timelineWidth = computed(() => {
  const range = timeRange.value;
  const hours = differenceInMilliseconds(range.end, range.start) / (1000 * 60 * 60);
  return hours * pixelsPerHour.value;
});

const timePeriods = computed(() => {
  const periods = [];
  const range = timeRange.value;
  let current = new Date(range.start);
  
  if (viewMode.value === 'Day') {
    while (current < range.end) {
      const x = getXFromTime(current);
      const width = pixelsPerHour.value * 24;
      periods.push({
        x,
        width,
        label: format(current, 'MMM d')
      });
      current = addDays(current, 1);
    }
  } else if (viewMode.value === 'Week') {
    while (current < range.end) {
      const x = getXFromTime(current);
      const width = pixelsPerHour.value * 24 * 7;
      periods.push({
        x,
        width,
        label: format(current, 'MMM d')
      });
      current = addDays(current, 7);
    }
  } else { // Month
    while (current < range.end) {
      const x = getXFromTime(current);
      const width = pixelsPerHour.value * 24 * 30;
      periods.push({
        x,
        width,
        label: format(current, 'MMM yyyy')
      });
      current = addDays(current, 30);
    }
  }
  
  return periods;
});

const todayX = computed(() => {
  return getXFromTime(new Date());
});

// Order colors
const orderColors = ref(new Map());

const getOrderColor = (orderId) => {
  if (!orderColors.value.has(orderId)) {
    const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#13c2c2', '#722ed1', '#eb2f96'];
    const colorIndex = orderColors.value.size % colors.length;
    orderColors.value.set(orderId, colors[colorIndex]);
  }
  return orderColors.value.get(orderId);
};

const getTaskColor = (task) => {
  if (task.locked) return '#909399';
  return getOrderColor(task.orderId);
};

// Positioning functions
const getXFromTime = (time) => {
  const range = timeRange.value;
  const millisFromStart = differenceInMilliseconds(new Date(time), range.start);
  const hours = millisFromStart / (1000 * 60 * 60);
  return hours * pixelsPerHour.value;
};

const getTimeFromX = (x) => {
  const range = timeRange.value;
  const hours = x / pixelsPerHour.value;
  const millis = hours * 60 * 60 * 1000;
  return new Date(range.start.getTime() + millis);
};

const getTaskX = (task) => {
  return getXFromTime(task.start);
};

const getTaskWidth = (task) => {
  const startX = getXFromTime(task.start);
  const endX = getXFromTime(task.end);
  return Math.max(endX - startX, 20); // Minimum width
};

// Helper functions
const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
};

// View mode functions
const changeViewMode = (mode) => {
  viewMode.value = mode;
  if (mode === 'Day') {
    pixelsPerHour.value = 40;
  } else if (mode === 'Week') {
    pixelsPerHour.value = 20;
  } else {
    pixelsPerHour.value = 5;
  }
};

const zoomIn = () => {
  pixelsPerHour.value = Math.min(pixelsPerHour.value * 1.5, 200);
};

const zoomOut = () => {
  pixelsPerHour.value = Math.max(pixelsPerHour.value / 1.5, 2);
};

const fitToScreen = () => {
  if (ganttContainer.value) {
    const containerWidth = ganttContainer.value.offsetWidth - 400; // Subtract list width
    const range = timeRange.value;
    const hours = differenceInMilliseconds(range.end, range.start) / (1000 * 60 * 60);
    pixelsPerHour.value = containerWidth / hours;
  }
};

// Task selection
const selectTask = (taskId) => {
  selectedTask.value = taskId;
  emit('task-selected', taskId);
};

const deselectTask = () => {
  selectedTask.value = null;
  emit('task-selected', null);
};

// Drag and drop
const startDrag = (event, task, rowIndex) => {
  if (task.locked) return;
  
  dragging.value = true;
  draggedTask.value = { ...task, rowIndex };
  dragStartX.value = event.clientX;
  dragStartTime.value = new Date(task.start);
  
  event.preventDefault();
};

const startResize = (event, task, mode) => {
  resizing.value = true;
  resizeMode.value = mode;
  draggedTask.value = { ...task };
  dragStartX.value = event.clientX;
  dragStartTime.value = new Date(mode === 'start' ? task.start : task.end);
  
  event.preventDefault();
};

const handleMouseMove = (event) => {
  if (!dragging.value && !resizing.value) return;
  
  const deltaX = event.clientX - dragStartX.value;
  const deltaTime = (deltaX / pixelsPerHour.value) * 60 * 60 * 1000;
  
  if (dragging.value) {
    // Move entire task
    const newStart = new Date(dragStartTime.value.getTime() + deltaTime);
    const duration = differenceInMilliseconds(
      new Date(draggedTask.value.end),
      new Date(draggedTask.value.start)
    );
    const newEnd = new Date(newStart.getTime() + duration);
    
    // Update visual feedback (could add preview)
    draggedTask.value.start = newStart.toISOString();
    draggedTask.value.end = newEnd.toISOString();
  } else if (resizing.value) {
    // Resize task
    if (resizeMode.value === 'start') {
      const newStart = new Date(dragStartTime.value.getTime() + deltaTime);
      if (newStart < new Date(draggedTask.value.end)) {
        draggedTask.value.start = newStart.toISOString();
      }
    } else {
      const newEnd = new Date(dragStartTime.value.getTime() + deltaTime);
      if (newEnd > new Date(draggedTask.value.start)) {
        draggedTask.value.end = newEnd.toISOString();
      }
    }
  }
};

const handleMouseUp = () => {
  if ((dragging.value || resizing.value) && draggedTask.value) {
    // Emit update
    emit('task-updated', {
      id: draggedTask.value.id,
      start: draggedTask.value.start,
      end: draggedTask.value.end
    });
  }
  
  dragging.value = false;
  resizing.value = false;
  resizeMode.value = null;
  draggedTask.value = null;
};

const handleScroll = (event) => {
  // Sync header scroll with body
  // Implementation depends on layout
};

// Lifecycle
onMounted(() => {
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp);
  
  // Auto-fit on mount
  setTimeout(fitToScreen, 100);
});

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mouseup', handleMouseUp);
});
</script>

<style scoped>
.gantt-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.gantt-toolbar {
  padding: 12px;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  background: #f5f7fa;
}

.gantt-chart-wrapper {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.gantt-grid {
  display: flex;
  height: 100%;
}

.gantt-list {
  width: 400px;
  border-right: 2px solid #dcdfe6;
  overflow: hidden;
  flex-shrink: 0;
  background: white;
}

.gantt-list-header {
  height: 40px;
  display: flex;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  font-weight: 600;
  font-size: 13px;
  color: #606266;
}

.gantt-list-body {
  overflow-y: auto;
  overflow-x: hidden;
}

.gantt-list-row {
  height: 50px;
  display: flex;
  border-bottom: 1px solid #f5f7fa;
  cursor: pointer;
  transition: background 0.2s;
}

.gantt-list-row:hover {
  background: #f5f7fa;
}

.gantt-list-row.selected {
  background: #ecf5ff;
  border-left: 3px solid #409eff;
}

.gantt-list-row.locked {
  opacity: 0.6;
}

.list-column {
  padding: 8px;
  display: flex;
  align-items: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
}

.order-col {
  width: 120px;
  flex-shrink: 0;
}

.operation-col {
  flex: 1;
  min-width: 150px;
}

.duration-col {
  width: 100px;
  flex-shrink: 0;
  justify-content: flex-end;
  color: #909399;
}

.gantt-timeline {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.gantt-timeline-header {
  height: 40px;
  border-bottom: 1px solid #dcdfe6;
  background: #f5f7fa;
  overflow: hidden;
}

.gantt-timeline-body {
  flex: 1;
  overflow: auto;
  background: white;
}

.task-bar {
  transition: stroke 0.2s;
}

.task-bar:hover {
  filter: brightness(1.1);
}

.task-bar.draggable {
  cursor: move;
}

.task-bar.locked {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
