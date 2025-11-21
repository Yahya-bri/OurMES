<template>
  <div class="traceability-page">
    <h1>Genealogy & Traceability</h1>

    <el-card>
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="Enter Batch / Serial Number"
          style="width: 300px; margin-right: 10px"
        />
        <el-button type="primary" @click="searchTraceability">Search</el-button>
      </div>
    </el-card>

    <div v-if="traceData" style="margin-top: 20px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card header="Backward Traceability (Ingredients/Components)">
            <el-timeline>
              <el-timeline-item
                v-for="(item, index) in traceData.backward"
                :key="index"
                :timestamp="item.timestamp"
                placement="top"
              >
                <el-card>
                  <h4>{{ item.material }}</h4>
                  <p>Batch: {{ item.batch }} | Supplier: {{ item.supplier }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card header="Forward Traceability (Distribution)">
            <el-timeline>
              <el-timeline-item
                v-for="(item, index) in traceData.forward"
                :key="index"
                :timestamp="item.timestamp"
                placement="top"
              >
                <el-card>
                  <h4>{{ item.customer }}</h4>
                  <p>Order: {{ item.order }} | Status: {{ item.status }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const searchQuery = ref("");
const traceData = ref(null);

const searchTraceability = () => {
  // Mock data response
  if (searchQuery.value) {
    traceData.value = {
      backward: [
        {
          timestamp: "2023-11-01 08:00",
          material: "Raw Steel",
          batch: "RS-998",
          supplier: "SteelCo Inc.",
        },
        {
          timestamp: "2023-11-02 10:30",
          material: "Paint Primer",
          batch: "PP-55",
          supplier: "ChemWorks",
        },
      ],
      forward: [
        {
          timestamp: "2023-11-10 14:00",
          customer: "AutoParts Ltd.",
          order: "ORD-5001",
          status: "Shipped",
        },
      ],
    };
  }
};
</script>

<style scoped>
.traceability-page {
  padding: 20px;
}
.search-bar {
  display: flex;
  align-items: center;
}
</style>
