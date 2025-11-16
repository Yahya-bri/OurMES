<template>
  <div class="production-lines-page">
    <div class="page-header">
      <h1>Production Lines</h1>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">
        New Production Line
      </el-button>
    </div>

    <div class="stats-container">
      <el-card class="stat-card stat-total">
        <div class="stat-content">
          <el-icon><Collection /></el-icon>
          <div>
            <div class="stat-label">Total Lines</div>
            <div class="stat-value">{{ stats.total }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card stat-active">
        <div class="stat-content">
          <el-icon><CircleCheck /></el-icon>
          <div>
            <div class="stat-label">Active</div>
            <div class="stat-value">{{ stats.active }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card stat-workstations">
        <div class="stat-content">
          <el-icon><Cpu /></el-icon>
          <div>
            <div class="stat-label">Workstations Assigned</div>
            <div class="stat-value">{{ stats.workstations }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <el-card>
      <div class="table-controls">
        <el-input
          v-model="searchQuery"
          :prefix-icon="Search"
          placeholder="Search production lines..."
          clearable
          style="width: 280px;"
        />
        <el-select
          v-model="statusFilter"
          placeholder="Status"
          clearable
          style="width: 180px;"
        >
          <el-option label="All" value="" />
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
        </el-select>
      </div>

      <el-table
        :data="filteredLines"
        v-loading="loading"
        style="width: 100%; margin-top: 15px;"
      >
        <el-table-column prop="number" label="Number" width="150" sortable />
        <el-table-column prop="name" label="Name" min-width="200" sortable />
        <el-table-column prop="description" label="Description" min-width="250" show-overflow-tooltip />
        <el-table-column label="Workstations" width="160">
          <template #default="{ row }">
            <el-tag size="small">{{ lineWorkstations(row).length }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="140">
          <template #default="{ row }">
            <el-switch
              v-model="row.active"
              @change="toggleActive(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" :icon="View" @click="openDetails(row)">
              Details
            </el-button>
            <el-button size="small" :icon="Edit" @click="openEditDialog(row)">
              Edit
            </el-button>
            <el-button
              size="small"
              type="danger"
              :icon="Delete"
              @click="deleteLine(row)"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="showDialog"
      :title="dialogMode === 'create' ? 'Create Production Line' : 'Edit Production Line'"
      width="560px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="140px"
      >
        <el-form-item label="Number" prop="number">
          <el-input v-model="form.number" />
        </el-form-item>
        <el-form-item label="Name" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input
            type="textarea"
            :rows="3"
            v-model="form.description"
          />
        </el-form-item>
        <el-form-item label="Active">
          <el-switch v-model="form.active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">
          {{ dialogMode === 'create' ? 'Create' : 'Update' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showDetailsDialog"
      title="Production Line Details"
      width="600px"
    >
      <div v-if="selectedLine">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Number">{{ selectedLine.number }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedLine.active ? 'success' : 'info'">
              {{ selectedLine.active ? 'Active' : 'Inactive' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Name">{{ selectedLine.name }}</el-descriptions-item>
          <el-descriptions-item label="Workstations">{{ lineWorkstations(selectedLine).length }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">
            {{ selectedLine.description || '—' }}
          </el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px;">Assigned Workstations</h4>
        <el-empty v-if="lineWorkstations(selectedLine).length === 0" description="No workstations assigned" />
        <el-table
          v-else
          :data="lineWorkstations(selectedLine)"
          style="width: 100%; margin-top: 10px;"
          size="small"
        >
          <el-table-column prop="number" label="Number" width="140" />
          <el-table-column prop="name" label="Name" min-width="180" />
          <el-table-column prop="description" label="Description" show-overflow-tooltip />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="showDetailsDialog = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  getProductionLines, 
  createProductionLine, 
  updateProductionLine, 
  deleteProductionLine, 
  getWorkstations 
} from '@/modules/basic-data/services/basicDataService';
import { Plus, Edit, Delete, View, Search, Collection, CircleCheck, Cpu } from '@element-plus/icons-vue';

const loading = ref(false);
const submitting = ref(false);
const productionLines = ref([]);
const workstations = ref([]);
const searchQuery = ref('');
const statusFilter = ref('');
const showDialog = ref(false);
const showDetailsDialog = ref(false);
const dialogMode = ref('create');
const selectedLine = ref(null);
const formRef = ref(null);

const form = reactive({
  id: null,
  number: '',
  name: '',
  description: '',
  active: true
});

const rules = {
  number: [{ required: true, message: 'Number is required', trigger: 'blur' }],
  name: [{ required: true, message: 'Name is required', trigger: 'blur' }]
};

const stats = reactive({
  total: 0,
  active: 0,
  workstations: 0
});

const normalizeListResponse = (payload) => {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.results)) return payload.results;
  if (Array.isArray(payload.items)) return payload.items;
  return [];
};

const filteredLines = computed(() => {
  let list = productionLines.value;
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    list = list.filter(line =>
      line.number.toLowerCase().includes(query) ||
      line.name.toLowerCase().includes(query) ||
      (line.description && line.description.toLowerCase().includes(query))
    );
  }
  if (statusFilter.value === 'active') {
    list = list.filter(line => line.active);
  } else if (statusFilter.value === 'inactive') {
    list = list.filter(line => !line.active);
  }
  return list;
});

const loadProductionLines = async () => {
  loading.value = true;
  try {
    productionLines.value = normalizeListResponse(await getProductionLines());
    calculateStats();
  } catch (error) {
    ElMessage.error('Failed to load production lines');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const loadWorkstations = async () => {
  try {
    workstations.value = normalizeListResponse(await getWorkstations());
    calculateStats();
  } catch (error) {
    console.error('Failed to load workstations', error);
  }
};

const calculateStats = () => {
  stats.total = productionLines.value.length;
  stats.active = productionLines.value.filter(line => line.active).length;
  stats.workstations = workstations.value.length;
};

const lineWorkstations = (line) => {
  const assignedIds = new Set(
    (line.workstations || []).map(ws => ws.id)
  );
  if (assignedIds.size === 0) {
    // fallback to global list based on production_line id
    return workstations.value.filter(ws => ws.production_line === line.id);
  }
  return (line.workstations || []);
};

const openCreateDialog = () => {
  dialogMode.value = 'create';
  resetForm();
  showDialog.value = true;
};

const openEditDialog = (line) => {
  dialogMode.value = 'edit';
  form.id = line.id;
  form.number = line.number;
  form.name = line.name;
  form.description = line.description || '';
  form.active = line.active;
  showDialog.value = true;
};

const openDetails = (line) => {
  selectedLine.value = line;
  showDetailsDialog.value = true;
};

const resetForm = () => {
  form.id = null;
  form.number = '';
  form.name = '';
  form.description = '';
  form.active = true;
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
      const payload = {
        number: form.number,
        name: form.name,
        description: form.description,
        active: form.active
      };
      if (dialogMode.value === 'create') {
        await createProductionLine(payload);
        ElMessage.success('Production line created');
      } else {
        await updateProductionLine(form.id, payload);
        ElMessage.success('Production line updated');
      }
      showDialog.value = false;
      await loadProductionLines();
    } catch (error) {
      ElMessage.error('Failed to save production line');
      console.error(error);
    } finally {
      submitting.value = false;
    }
  });
};

const deleteLine = async (line) => {
  const assigned = lineWorkstations(line);
  if (assigned.length > 0) {
    ElMessage.warning('Remove or reassign workstations before deleting this line.');
    return;
  }
  try {
    await ElMessageBox.confirm(
      `Delete production line "${line.name}"?`,
      'Confirm Delete',
      { type: 'warning' }
    );
    await deleteProductionLine(line.id);
    ElMessage.success('Production line deleted');
    await loadProductionLines();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete production line');
      console.error(error);
    }
  }
};

const toggleActive = async (line) => {
  try {
    await updateProductionLine(line.id, { active: line.active });
    ElMessage.success(`Line ${line.active ? 'activated' : 'deactivated'}`);
  } catch (error) {
    line.active = !line.active;
    ElMessage.error('Failed to update status');
    console.error(error);
  }
};

onMounted(() => {
  loadProductionLines();
  loadWorkstations();
});
</script>

<style scoped>
.production-lines-page {
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

.stats-container {
  display: grid;
  gap: 15px;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  margin-bottom: 20px;
}

.stat-card {
  border-left: 4px solid #409eff;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
}

.stat-content .el-icon {
  font-size: 28px;
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-active {
  border-left-color: #67c23a;
}

.stat-workstations {
  border-left-color: #e6a23c;
}

.table-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
