<template>
  <div class="ncr-page">
    <h1>Non-Conformance Management (NCR)</h1>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>Active NCRs</span>
          <el-button type="danger" @click="createNCR">Create NCR</el-button>
        </div>
      </template>
      <el-table :data="ncrList" style="width: 100%">
        <el-table-column prop="id" label="NCR ID" width="120" />
        <el-table-column prop="product" label="Product" />
        <el-table-column prop="issue" label="Issue Description" />
        <el-table-column prop="status" label="Status">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{
              scope.row.status
            }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Disposition">
          <template #default="scope">
            <el-select
              v-model="scope.row.disposition"
              placeholder="Select"
              size="small"
              @change="updateDisposition(scope.row)"
            >
              <el-option label="Rework" value="Rework" />
              <el-option label="Scrap" value="Scrap" />
              <el-option label="Use As Is" value="Use As Is" />
            </el-select>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";

const ncrList = ref([
  {
    id: "NCR-2023-055",
    product: "Gear Shaft",
    issue: "Surface scratch > 2mm",
    status: "Quarantine",
    disposition: "",
  },
  {
    id: "NCR-2023-058",
    product: "Housing",
    issue: "Porosity detected",
    status: "Review",
    disposition: "Scrap",
  },
]);

const getStatusType = (status) => {
  const map = {
    Quarantine: "danger",
    Review: "warning",
    Closed: "success",
  };
  return map[status] || "info";
};

const createNCR = () => {
  ElMessage.info("Create NCR dialog would open here.");
};

const updateDisposition = (row) => {
  ElMessage.success(`Disposition for ${row.id} updated to ${row.disposition}`);
};
</script>

<style scoped>
.ncr-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
