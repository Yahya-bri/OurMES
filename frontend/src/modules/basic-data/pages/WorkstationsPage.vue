<template>
  <div class="workstations-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1>Workstations Management</h1>
      <div class="header-actions">
        <el-button 
          type="primary" 
          :icon="Plus" 
          @click="openCreateDialog"
        >
          New Workstation
        </el-button>
        <el-dropdown @command="handleExport" trigger="click">
          <el-button :icon="Download">
            Export <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="csv">Export to CSV</el-dropdown-item>
              <el-dropdown-item command="excel">Export to Excel</el-dropdown-item>
              <el-dropdown-item command="pdf">Export to PDF</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- Stats Dashboard -->
    <div class="stats-container">
      <el-card shadow="hover" class="stat-card stat-total">
        <div class="stat-content">
          <el-icon class="stat-icon" color="#409eff"><Box /></el-icon>
          <div class="stat-info">
            <div class="stat-label">Total Workstations</div>
            <div class="stat-value">{{ stats.total }}</div>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="hover" class="stat-card stat-active">
        <div class="stat-content">
          <el-icon class="stat-icon" color="#67c23a"><SuccessFilled /></el-icon>
          <div class="stat-info">
            <div class="stat-label">Active</div>
            <div class="stat-value">{{ stats.active }}</div>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="hover" class="stat-card stat-lines">
        <div class="stat-content">
          <el-icon class="stat-icon" color="#e6a23c"><Connection /></el-icon>
          <div class="stat-info">
            <div class="stat-label">In Production Lines</div>
            <div class="stat-value">{{ stats.inProductionLines }}</div>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="hover" class="stat-card stat-utilization">
        <div class="stat-content">
          <el-icon class="stat-icon" color="#909399"><DataLine /></el-icon>
          <div class="stat-info">
            <div class="stat-label">Utilization Rate</div>
            <div class="stat-value">{{ stats.utilization }}%</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Filters and Table -->
    <el-card>
      <div class="table-controls">
        <div class="filters">
          <el-input
            v-model="searchQuery"
            placeholder="Search workstations..."
            :prefix-icon="Search"
            clearable
            style="width: 300px;"
            @input="handleSearch"
          />
          <el-select
            v-model="statusFilter"
            placeholder="Status"
            clearable
            style="width: 150px;"
            @change="handleSearch"
          >
            <el-option label="All Status" value="" />
            <el-option label="Active" value="active" />
            <el-option label="Inactive" value="inactive" />
          </el-select>
          <el-select
            v-model="productionLineFilter"
            placeholder="Production Line"
            clearable
            style="width: 200px;"
            @change="handleSearch"
          >
            <el-option label="All Lines" value="" />
            <el-option 
              v-for="line in productionLines" 
              :key="line.id" 
              :label="line.name" 
              :value="line.id"
            />
          </el-select>
        </div>
        <div class="bulk-actions">
          <el-button 
            v-if="selectedWorkstations.length > 0"
            :icon="Edit"
            @click="bulkActivate"
          >
            Activate ({{ selectedWorkstations.length }})
          </el-button>
          <el-button 
            v-if="selectedWorkstations.length > 0"
            :icon="Edit"
            @click="bulkDeactivate"
          >
            Deactivate ({{ selectedWorkstations.length }})
          </el-button>
          <el-button 
            v-if="selectedWorkstations.length > 0"
            type="danger"
            :icon="Delete"
            @click="bulkDelete"
          >
            Delete ({{ selectedWorkstations.length }})
          </el-button>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="filteredWorkstations"
        style="width: 100%; margin-top: 20px;"
        @selection-change="handleSelectionChange"
        stripe
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="number" label="Number" sortable width="150" />
        <el-table-column prop="name" label="Name" sortable min-width="200" />
        <el-table-column prop="description" label="Description" min-width="250">
          <template #default="{ row }">
            <el-text truncated style="max-width: 100%;">{{ row.description || '-' }}</el-text>
          </template>
        </el-table-column>
        <el-table-column label="Production Line" width="200">
          <template #default="{ row }">
            <el-tag v-if="row.production_line_name" size="small">
              {{ row.production_line_name }}
            </el-tag>
            <span v-else class="muted-text">Unassigned</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.active"
              @change="toggleActive(row)"
              active-text="Active"
              inactive-text="Inactive"
            />
          </template>
        </el-table-column>
        <el-table-column label="Created" width="150" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              :icon="Edit"
              @click="openEditDialog(row)"
            >
              Edit
            </el-button>
            <el-button
              size="small"
              type="danger"
              :icon="Delete"
              @click="deleteWorkstation(row)"
            />
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 25, 50, 100]"
          :total="filteredWorkstations.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="dialogMode === 'create' ? 'Create Workstation' : 'Edit Workstation'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="140px"
      >
        <el-form-item label="Number" prop="number">
          <el-input v-model="form.number" placeholder="e.g., WS001" />
        </el-form-item>

        <el-form-item label="Name" prop="name">
          <el-input v-model="form.name" placeholder="Workstation name" />
        </el-form-item>

        <el-form-item label="Description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="Optional description"
          />
        </el-form-item>

        <el-form-item label="Production Line" prop="production_line">
          <el-select
            v-model="form.production_line"
            placeholder="Select production line"
            style="width: 100%;"
            filterable
          >
            <el-option
              v-for="line in productionLines"
              :key="line.id"
              :label="line.name"
              :value="line.id"
            />
          </el-select>
          <div class="form-help-text">
            Each workstation must belong to exactly one production line.
          </div>
        </el-form-item>

        <el-form-item label="Active">
          <el-switch v-model="form.active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ dialogMode === 'create' ? 'Create' : 'Update' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  Plus, Edit, Delete, Search, Download, ArrowDown,
  Box, SuccessFilled, Connection, DataLine
} from '@element-plus/icons-vue';
import { 
  getWorkstations, 
  createWorkstation, 
  updateWorkstation, 
  deleteWorkstation as deleteWorkstationAPI,
  getProductionLines 
} from '@/modules/basic-data/services/basicDataService';

// Data
const loading = ref(false);
const submitting = ref(false);
const workstations = ref([]);
const productionLines = ref([]);
const selectedWorkstations = ref([]);
const showDialog = ref(false);
const dialogMode = ref('create');
const formRef = ref(null);

// Filters
const searchQuery = ref('');
const statusFilter = ref('');
const productionLineFilter = ref('');
const currentPage = ref(1);
const pageSize = ref(25);

// Stats
const stats = reactive({
  total: 0,
  active: 0,
  inProductionLines: 0,
  utilization: 0
});

// Form
const form = reactive({
  number: '',
  name: '',
  description: '',
  active: true,
  production_line: null
});

const rules = {
  number: [
    { required: true, message: 'Number is required', trigger: 'blur' }
  ],
  name: [
    { required: true, message: 'Name is required', trigger: 'blur' }
  ],
  production_line: [
    { required: true, message: 'Production line is required', trigger: 'change' }
  ]
};

const normalizeListResponse = (payload) => {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.results)) return payload.results;
  if (Array.isArray(payload.items)) return payload.items;
  return [];
};

// Computed
const filteredWorkstations = computed(() => {
  let result = workstations.value;

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(ws =>
      ws.number.toLowerCase().includes(query) ||
      ws.name.toLowerCase().includes(query) ||
      (ws.description && ws.description.toLowerCase().includes(query))
    );
  }

  // Status filter
  if (statusFilter.value === 'active') {
    result = result.filter(ws => ws.active);
  } else if (statusFilter.value === 'inactive') {
    result = result.filter(ws => !ws.active);
  }

  // Production line filter
  if (productionLineFilter.value) {
    const lineId = parseInt(productionLineFilter.value);
    result = result.filter(ws => ws.production_line === lineId);
  }

  return result;
});

// Methods
const loadWorkstations = async () => {
  loading.value = true;
  try {
    workstations.value = normalizeListResponse(await getWorkstations());
    calculateStats();
  } catch (error) {
    ElMessage.error('Failed to load workstations');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const loadProductionLines = async () => {
  try {
    productionLines.value = normalizeListResponse(await getProductionLines());
  } catch (error) {
    console.error('Failed to load production lines:', error);
  }
};

const calculateStats = () => {
  stats.total = workstations.value.length;
  stats.active = workstations.value.filter(ws => ws.active).length;
  
  // Count workstations that are linked to a production line
  stats.inProductionLines = workstations.value.filter(ws => Boolean(ws.production_line)).length;
  
  // Calculate utilization (percentage of workstations in production lines)
  stats.utilization = stats.total > 0 
    ? Math.round((stats.inProductionLines / stats.total) * 100) 
    : 0;
};

const getProductionLineName = (lineId) => {
  const line = productionLines.value.find(item => item.id === lineId);
  return line ? line.name : '';
};

const handleSearch = () => {
  currentPage.value = 1;
};

const handleSelectionChange = (selection) => {
  selectedWorkstations.value = selection;
};

const openCreateDialog = () => {
  dialogMode.value = 'create';
  resetForm();
  showDialog.value = true;
};

const openEditDialog = (workstation) => {
  dialogMode.value = 'edit';
  form.id = workstation.id;
  form.number = workstation.number;
  form.name = workstation.name;
  form.description = workstation.description || '';
  form.active = workstation.active;
  
  form.production_line = workstation.production_line || null;
  
  showDialog.value = true;
};

const resetForm = () => {
  form.id = null;
  form.number = '';
  form.name = '';
  form.description = '';
  form.active = true;
  form.production_line = null;
  if (formRef.value) {
    formRef.value.clearValidate();
  }
};

const submitForm = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return;
    
    submitting.value = true;
    try {
      const workstationData = {
        number: form.number,
        name: form.name,
        description: form.description,
        active: form.active,
        production_line: form.production_line
      };
      
      let savedWorkstation;
      if (dialogMode.value === 'create') {
        savedWorkstation = await createWorkstation(workstationData);
        ElMessage.success('Workstation created successfully');
      } else {
        savedWorkstation = await updateWorkstation(form.id, workstationData);
        ElMessage.success('Workstation updated successfully');
      }
      
      showDialog.value = false;
      await loadWorkstations();
      await loadProductionLines();
    } catch (error) {
      ElMessage.error(`Failed to ${dialogMode.value} workstation`);
      console.error(error);
    } finally {
      submitting.value = false;
    }
  });
};

const toggleActive = async (workstation) => {
  try {
    await updateWorkstation(workstation.id, { 
      active: workstation.active 
    });
    ElMessage.success(`Workstation ${workstation.active ? 'activated' : 'deactivated'}`);
    calculateStats();
  } catch (error) {
    workstation.active = !workstation.active;
    ElMessage.error('Failed to update workstation status');
    console.error(error);
  }
};

const deleteWorkstation = async (workstation) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete workstation "${workstation.name}"?`,
      'Confirm Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    );
    
    await deleteWorkstationAPI(workstation.id);
    ElMessage.success('Workstation deleted successfully');
    await loadWorkstations();
    await loadProductionLines();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete workstation');
      console.error(error);
    }
  }
};

const bulkActivate = async () => {
  try {
    for (const ws of selectedWorkstations.value) {
      await updateWorkstation(ws.id, { active: true });
    }
    ElMessage.success(`Activated ${selectedWorkstations.value.length} workstations`);
    await loadWorkstations();
  } catch (error) {
    ElMessage.error('Failed to activate workstations');
    console.error(error);
  }
};

const bulkDeactivate = async () => {
  try {
    for (const ws of selectedWorkstations.value) {
      await updateWorkstation(ws.id, { active: false });
    }
    ElMessage.success(`Deactivated ${selectedWorkstations.value.length} workstations`);
    await loadWorkstations();
  } catch (error) {
    ElMessage.error('Failed to deactivate workstations');
    console.error(error);
  }
};

const bulkDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete ${selectedWorkstations.value.length} workstations?`,
      'Confirm Bulk Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    );
    
    for (const ws of selectedWorkstations.value) {
      await deleteWorkstationAPI(ws.id);
    }
    ElMessage.success(`Deleted ${selectedWorkstations.value.length} workstations`);
    await loadWorkstations();
    await loadProductionLines();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete workstations');
      console.error(error);
    }
  }
};

const handleExport = (format) => {
  if (filteredWorkstations.value.length === 0) {
    ElMessage.warning('No data to export');
    return;
  }
  
  switch (format) {
    case 'csv':
      exportToCSV();
      break;
    case 'excel':
      ElMessage.info('Excel export coming soon');
      break;
    case 'pdf':
      ElMessage.info('PDF export coming soon');
      break;
  }
};

const exportToCSV = () => {
  const headers = ['Number', 'Name', 'Description', 'Production Line', 'Status', 'Created'];
  const rows = filteredWorkstations.value.map(ws => [
    ws.number,
    ws.name,
    ws.description || '',
    getProductionLineName(ws.production_line) || '',
    ws.active ? 'Active' : 'Inactive',
    formatDate(ws.created_at)
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `workstations_${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
  
  ElMessage.success('CSV exported successfully');
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

// Lifecycle
onMounted(() => {
  loadWorkstations();
  loadProductionLines();
});
</script>

<style scoped>
.workstations-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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
  margin-bottom: 20px;
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

.stat-active {
  border-left: 4px solid #67c23a;
}

.stat-lines {
  border-left: 4px solid #e6a23c;
}

.stat-utilization {
  border-left: 4px solid #909399;
}

/* Table Controls */
.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.bulk-actions {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.form-help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.muted-text {
  color: #909399;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-container {
    grid-template-columns: 1fr;
  }
  
  .table-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters {
    width: 100%;
  }
  
  .bulk-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
