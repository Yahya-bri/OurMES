<template>
  <div class="operations">
    <h1>Operations Management</h1>
    
    <!-- Stats Dashboard -->
    <div class="stats-container">
      <el-card class="stat-card stat-total">
        <div class="stat-content">
          <div class="stat-icon">⚙️</div>
          <div class="stat-info">
            <div class="stat-label">Total Operations</div>
            <div class="stat-value">{{ stats.total }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card stat-active">
        <div class="stat-content">
          <div class="stat-icon">✓</div>
          <div class="stat-info">
            <div class="stat-label">Active Operations</div>
            <div class="stat-value">{{ stats.active }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card stat-workstations">
        <div class="stat-content">
          <div class="stat-icon">🏭</div>
          <div class="stat-info">
            <div class="stat-label">With Workstations</div>
            <div class="stat-value">{{ stats.with_workstations }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card stat-avg-time">
        <div class="stat-content">
          <div class="stat-icon">⏱️</div>
          <div class="stat-info">
            <div class="stat-label">Avg. Batch Time</div>
            <div class="stat-value">{{ formatTime(stats.avg_tj) }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <el-card>
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button v-if="canEdit" type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> Create Operation
          </el-button>
          
          <el-dropdown v-if="canEdit && selectedOperations.length > 0" @command="handleBulkAction" style="margin-left: 10px;">
            <el-button>
              Bulk Actions ({{ selectedOperations.length }}) <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="activate">Activate</el-dropdown-item>
                <el-dropdown-item command="deactivate">Deactivate</el-dropdown-item>
                <el-dropdown-item divided command="delete" style="color: #f56c6c;">Delete</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <el-button @click="exportToCSV" style="margin-left: 10px;">
            <el-icon><Download /></el-icon> Export CSV
          </el-button>
        </div>
        
        <div class="toolbar-right">
          <el-input
            v-model="searchQuery"
            placeholder="Search operations..."
            style="width: 250px;"
            @input="handleSearch"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select v-model="filterActive" placeholder="Status" @change="loadOperations" style="margin-left: 10px; width: 120px;" clearable>
            <el-option label="All" value="" />
            <el-option label="Active" value="true" />
            <el-option label="Inactive" value="false" />
          </el-select>
        </div>
      </div>

      <!-- Operations Table -->
      <el-table 
        :data="operations" 
        style="width: 100%; margin-top: 20px;" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="number" label="Number" width="140" sortable />
        <el-table-column prop="name" label="Name" min-width="200" />
        <el-table-column label="Times" width="200">
          <template #default="scope">
            <div style="font-size: 12px; line-height: 1.5;">
              <div><strong>TJ:</strong> {{ formatTime(scope.row.tj) }}</div>
              <div><strong>TPZ:</strong> {{ formatTime(scope.row.tpz) }}</div>
              <div><strong>Next:</strong> {{ formatTime(scope.row.time_next_operation) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Workstations" min-width="200">
          <template #default="scope">
            <div v-if="scope.row.workstation_names?.length" style="font-size: 12px;">
              <el-tag 
                v-for="(ws, idx) in scope.row.workstation_names.slice(0, 3)" 
                :key="idx" 
                size="small" 
                style="margin: 2px;"
              >
                {{ ws }}
              </el-tag>
              <span v-if="scope.row.workstation_names.length > 3" style="color: #909399; margin-left: 5px;">
                +{{ scope.row.workstation_names.length - 3 }} more
              </span>
            </div>
            <span v-else style="color: #909399; font-size: 12px;">No workstations</span>
          </template>
        </el-table-column>
        <el-table-column label="Active" width="80" align="center">
          <template #default="scope">
            <el-switch 
              v-model="scope.row.active" 
              @change="toggleActive(scope.row)"
              :disabled="!canEdit"
            />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewOperation(scope.row)">
              <el-icon><View /></el-icon> View
            </el-button>
            <el-button v-if="canEdit" size="small" type="primary" @click="editOperation(scope.row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button v-if="canEdit" size="small" type="danger" @click="deleteOp(scope.row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next, jumper"
        @current-change="loadOperations"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingOperation ? 'Edit Operation' : 'Create Operation'" 
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="operationForm" label-width="180px" style="padding: 10px 20px;">
        <el-form-item label="Number" required>
          <el-input v-model="operationForm.number" placeholder="e.g., OP-001" />
        </el-form-item>
        <el-form-item label="Name" required>
          <el-input v-model="operationForm.name" placeholder="Operation name" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="operationForm.description" type="textarea" :rows="4" placeholder="Describe the operation..." />
        </el-form-item>
        
        <el-divider content-position="left">Time Parameters</el-divider>
        
        <el-form-item label="TJ - Batch Time (s)">
          <el-input-number 
            v-model="operationForm.tj" 
            :min="0" 
            :step="1"
            style="width: 100%;"
          />
          <span style="display: block; font-size: 12px; color: #909399; margin-top: 5px;">
            Time required to process one batch
          </span>
        </el-form-item>
        
        <el-form-item label="TPZ - Preparation Time (s)">
          <el-input-number 
            v-model="operationForm.tpz" 
            :min="0" 
            :step="1"
            style="width: 100%;"
          />
          <span style="display: block; font-size: 12px; color: #909399; margin-top: 5px;">
            Setup and preparation time before operation starts
          </span>
        </el-form-item>
        
        <el-form-item label="Time to Next Op. (s)">
          <el-input-number 
            v-model="operationForm.time_next_operation" 
            :min="0" 
            :step="1"
            style="width: 100%;"
          />
          <span style="display: block; font-size: 12px; color: #909399; margin-top: 5px;">
            Transition time to the next operation
          </span>
        </el-form-item>
        
        <el-divider content-position="left">Workstations</el-divider>
        
        <el-form-item label="Assigned Workstations">
          <el-select 
            v-model="operationForm.workstations" 
            multiple 
            filterable 
            placeholder="Select workstations"
            style="width: 100%;"
          >
            <el-option 
              v-for="ws in workstations" 
              :key="ws.id" 
              :label="`${ws.number} - ${ws.name}`" 
              :value="ws.id" 
            />
          </el-select>
          <span style="display: block; font-size: 12px; color: #909399; margin-top: 5px;">
            Workstations where this operation can be performed
          </span>
        </el-form-item>
        
        <el-form-item label="Active">
          <el-switch v-model="operationForm.active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeDialog">Cancel</el-button>
        <el-button type="primary" @click="saveOperation" :loading="saving">
          {{ editingOperation ? 'Update' : 'Create' }} Operation
        </el-button>
      </template>
    </el-dialog>

    <!-- Operation Details Dialog -->
    <el-dialog v-model="showDetailsDialog" title="Operation Details" width="700px">
      <el-descriptions v-if="selectedOperation" :column="2" border>
        <el-descriptions-item label="Number">{{ selectedOperation.number }}</el-descriptions-item>
        <el-descriptions-item label="Name">{{ selectedOperation.name }}</el-descriptions-item>
        <el-descriptions-item label="TJ (Batch Time)">{{ formatTime(selectedOperation.tj) }}</el-descriptions-item>
        <el-descriptions-item label="TPZ (Prep Time)">{{ formatTime(selectedOperation.tpz) }}</el-descriptions-item>
        <el-descriptions-item label="Time to Next Op.">{{ formatTime(selectedOperation.time_next_operation) }}</el-descriptions-item>
        <el-descriptions-item label="Active">
          <el-tag :type="selectedOperation.active ? 'success' : 'info'">
            {{ selectedOperation.active ? 'Active' : 'Inactive' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Workstations" :span="2">
          <div v-if="selectedOperation.workstation_names?.length">
            <el-tag 
              v-for="(ws, idx) in selectedOperation.workstation_names" 
              :key="idx" 
              style="margin: 2px;"
            >
              {{ ws }}
            </el-tag>
          </div>
          <span v-else style="color: #909399;">No workstations assigned</span>
        </el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">
          {{ selectedOperation.description || 'No description' }}
        </el-descriptions-item>
        <el-descriptions-item label="Created">{{ formatDate(selectedOperation.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="Updated">{{ formatDate(selectedOperation.updated_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  Plus, Search, ArrowDown, View, Edit, Delete, Download
} from '@element-plus/icons-vue';
import { 
  getOperations, createOperation, updateOperation, deleteOperation
} from '../services/routingService';
import { getWorkstations } from '@/modules/basic-data/services/basicDataService';
import { useAuthStore } from '@/modules/auth/stores/authStore';

// Data
const operations = ref([]);
const workstations = ref([]);
const stats = ref({ total: 0, active: 0, with_workstations: 0, avg_tj: 0 });
const loading = ref(false);
const saving = ref(false);
const searchQuery = ref('');
const filterActive = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const selectedOperations = ref([]);

// Dialogs
const showCreateDialog = ref(false);
const showDetailsDialog = ref(false);

// Forms
const editingOperation = ref(null);
const selectedOperation = ref(null);

const operationForm = ref({
  number: '',
  name: '',
  description: '',
  tj: 0,
  tpz: 0,
  time_next_operation: 0,
  workstations: [],
  active: true,
});

// Auth
const auth = useAuthStore();
const canEdit = computed(() => auth.hasRole(['Supervisor', 'Admin']));

// Methods
const formatTime = (seconds) => {
  if (!seconds || seconds === 0) return '0s';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  const parts = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);
  
  return parts.join(' ');
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString();
};

const calculateStats = () => {
  const total = operations.value.length;
  const active = operations.value.filter(op => op.active).length;
  const with_workstations = operations.value.filter(op => op.workstation_names?.length > 0).length;
  const avg_tj = total > 0 
    ? Math.round(operations.value.reduce((sum, op) => sum + (op.tj || 0), 0) / total)
    : 0;
  
  stats.value = { total, active, with_workstations, avg_tj };
};

const loadOperations = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      search: searchQuery.value,
    };
    
    if (filterActive.value !== '') {
      params.active = filterActive.value === 'true';
    }
    
    const data = await getOperations(params);
    operations.value = data.results || data;
    total.value = data.count || operations.value.length;
    calculateStats();
  } catch (error) {
    ElMessage.error('Failed to load operations');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const loadWorkstations = async () => {
  try {
    const data = await getWorkstations();
    workstations.value = data.results || data;
  } catch (error) {
    console.error('Failed to load workstations:', error);
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  loadOperations();
};

const handleSelectionChange = (selection) => {
  selectedOperations.value = selection;
};

const openCreateDialog = () => {
  editingOperation.value = null;
  operationForm.value = {
    number: '',
    name: '',
    description: '',
    tj: 0,
    tpz: 0,
    time_next_operation: 0,
    workstations: [],
    active: true,
  };
  showCreateDialog.value = true;
};

const closeDialog = () => {
  showCreateDialog.value = false;
  editingOperation.value = null;
};

const viewOperation = (operation) => {
  selectedOperation.value = operation;
  showDetailsDialog.value = true;
};

const editOperation = (operation) => {
  editingOperation.value = operation;
  operationForm.value = { 
    ...operation,
    workstations: operation.workstations || [],
    active: operation.active !== false
  };
  showCreateDialog.value = true;
};

const saveOperation = async () => {
  if (!operationForm.value.number || !operationForm.value.name) {
    ElMessage.warning('Please fill in required fields: Number and Name');
    return;
  }

  saving.value = true;
  try {
    if (editingOperation.value) {
      await updateOperation(editingOperation.value.id, operationForm.value);
      ElMessage.success('Operation updated successfully');
    } else {
      await createOperation(operationForm.value);
      ElMessage.success('Operation created successfully');
    }
    closeDialog();
    loadOperations();
  } catch (error) {
    ElMessage.error('Failed to save operation');
    console.error(error);
  } finally {
    saving.value = false;
  }
};

const toggleActive = async (operation) => {
  try {
    await updateOperation(operation.id, { active: operation.active });
    ElMessage.success(`Operation ${operation.active ? 'activated' : 'deactivated'}`);
    calculateStats();
  } catch (error) {
    ElMessage.error('Failed to update operation');
    operation.active = !operation.active; // Revert on error
  }
};

const deleteOp = async (operation) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete operation "${operation.name}"? This may affect routings using this operation.`,
      'Delete Operation',
      { type: 'error' }
    );
    await deleteOperation(operation.id);
    ElMessage.success('Operation deleted');
    loadOperations();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete operation');
    }
  }
};

const handleBulkAction = async (command) => {
  if (selectedOperations.value.length === 0) {
    ElMessage.warning('No operations selected');
    return;
  }

  const ids = selectedOperations.value.map(op => op.id);

  try {
    switch (command) {
      case 'activate':
        await Promise.all(ids.map(id => updateOperation(id, { active: true })));
        ElMessage.success(`${ids.length} operations activated`);
        break;
      case 'deactivate':
        await Promise.all(ids.map(id => updateOperation(id, { active: false })));
        ElMessage.success(`${ids.length} operations deactivated`);
        break;
      case 'delete':
        await ElMessageBox.confirm(
          `Are you sure you want to delete ${ids.length} selected operations?`,
          'Bulk Delete',
          { type: 'error' }
        );
        await Promise.all(ids.map(id => deleteOperation(id)));
        ElMessage.success(`${ids.length} operations deleted`);
        break;
    }
    loadOperations();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to perform bulk action');
    }
  }
};

const exportToCSV = () => {
  if (operations.value.length === 0) {
    ElMessage.warning('No data to export');
    return;
  }

  const headers = ['Number', 'Name', 'TJ (s)', 'TPZ (s)', 'Time to Next (s)', 'Workstations', 'Active'];
  const rows = operations.value.map(op => [
    op.number,
    op.name,
    op.tj || 0,
    op.tpz || 0,
    op.time_next_operation || 0,
    (op.workstation_names || []).join('; '),
    op.active ? 'Yes' : 'No'
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `operations_${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
  
  ElMessage.success('CSV exported successfully');
};

onMounted(() => {
  loadOperations();
  loadWorkstations();
});
</script>

<style scoped>
.operations {
  padding: 20px;
}

/* Stats Dashboard */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 32px;
  line-height: 1;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-total {
  border-left: 4px solid #409eff;
}

.stat-active {
  border-left: 4px solid #67c23a;
}

.stat-workstations {
  border-left: 4px solid #e6a23c;
}

.stat-avg-time {
  border-left: 4px solid #909399;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

/* Form Hints */
:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-dialog__body) {
  padding-top: 10px;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-container {
    grid-template-columns: 1fr;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: flex-start;
  }
  
  .stat-value {
    font-size: 24px;
  }
}
</style>
