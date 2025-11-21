<template>
  <div class="inventory-page">
    <h1>Inventory Visibility</h1>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>Warehouse Stock</span>
          </template>
          <el-table :data="warehouseStock" style="width: 100%" height="250">
            <el-table-column prop="material" label="Material" />
            <el-table-column prop="quantity" label="Qty" />
            <el-table-column prop="unit" label="Unit" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>Shop Floor Stock</span>
          </template>
          <el-table :data="shopFloorStock" style="width: 100%" height="250">
            <el-table-column prop="material" label="Material" />
            <el-table-column prop="location" label="Loc" />
            <el-table-column prop="quantity" label="Qty" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>Buffer Zones</span>
          </template>
          <el-table :data="bufferStock" style="width: 100%" height="250">
            <el-table-column prop="zone" label="Zone" />
            <el-table-column prop="material" label="Material" />
            <el-table-column prop="quantity" label="Qty" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Aging & Expiration (FIFO/FEFO)</span>
          </template>
          <el-table :data="expiringMaterials" style="width: 100%">
            <el-table-column prop="batch" label="Batch #" />
            <el-table-column prop="material" label="Material" />
            <el-table-column prop="expiryDate" label="Expiry Date" />
            <el-table-column label="Status">
              <template #default="scope">
                <el-tag :type="getExpiryStatus(scope.row.daysRemaining)">
                  {{ scope.row.daysRemaining }} days left
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Action">
              <template #default="scope">
                <el-button
                  size="small"
                  type="danger"
                  v-if="scope.row.daysRemaining <= 0"
                  >Lock</el-button
                >
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Container Management</span>
          </template>
          <el-table :data="containers" style="width: 100%">
            <el-table-column prop="id" label="Container ID" />
            <el-table-column prop="type" label="Type" />
            <el-table-column prop="contents" label="Contents" />
            <el-table-column prop="location" label="Current Location" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from "vue";

const warehouseStock = ref([
  { material: "Steel Sheet 2mm", quantity: 500, unit: "pcs" },
  { material: "Plastic Granules", quantity: 1200, unit: "kg" },
  { material: "Bolts M8", quantity: 5000, unit: "pcs" },
]);

const shopFloorStock = ref([
  { material: "Steel Sheet 2mm", location: "Laser Cut", quantity: 50 },
  {
    material: "Plastic Granules",
    location: "Injection Molding",
    quantity: 200,
  },
]);

const bufferStock = ref([
  { zone: "Assembly Buffer", material: "Machined Parts", quantity: 15 },
  { zone: "Paint Buffer", material: "Assembled Units", quantity: 8 },
]);

const expiringMaterials = ref([
  {
    batch: "B-2023-001",
    material: "Adhesive X",
    expiryDate: "2023-12-01",
    daysRemaining: 12,
  },
  {
    batch: "B-2023-002",
    material: "Catalyst Y",
    expiryDate: "2023-11-15",
    daysRemaining: -4,
  },
  {
    batch: "B-2023-003",
    material: "Paint Z",
    expiryDate: "2024-01-20",
    daysRemaining: 62,
  },
]);

const containers = ref([
  {
    id: "BIN-101",
    type: "Bin",
    contents: "Bolts M8",
    location: "Warehouse A1",
  },
  {
    id: "PAL-205",
    type: "Pallet",
    contents: "Finished Goods",
    location: "Shipping Dock",
  },
  {
    id: "TOTE-055",
    type: "Tote",
    contents: "Sub-assemblies",
    location: "Assembly Line 1",
  },
]);

const getExpiryStatus = (days) => {
  if (days <= 0) return "danger";
  if (days <= 30) return "warning";
  return "success";
};
</script>

<style scoped>
.inventory-page {
  padding: 20px;
}
</style>
