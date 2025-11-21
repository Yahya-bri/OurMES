<template>
  <div class="root-cause-page">
    <h1>Root Cause Analysis Tools</h1>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>Compare Run vs Golden Run</span>
          </template>

          <el-form :inline="true" class="demo-form-inline">
            <el-form-item label="Select Run">
              <el-select
                v-model="selectedRun"
                placeholder="Select a production run"
              >
                <el-option label="Run #1023 (Yesterday)" value="1023" />
                <el-option label="Run #1022 (2 days ago)" value="1022" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="compareRuns">Compare</el-button>
            </el-form-item>
          </el-form>

          <div v-if="comparisonResult" class="comparison-result">
            <el-divider />
            <h3>Analysis Result</h3>
            <el-table :data="comparisonResult" style="width: 100%">
              <el-table-column prop="parameter" label="Parameter" />
              <el-table-column prop="golden" label="Golden Run Value" />
              <el-table-column prop="actual" label="Selected Run Value" />
              <el-table-column prop="deviation" label="Deviation">
                <template #default="scope">
                  <el-tag
                    :type="scope.row.deviation > 5 ? 'danger' : 'success'"
                  >
                    {{ scope.row.deviation }}%
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from "vue";

const selectedRun = ref("");
const comparisonResult = ref(null);

const compareRuns = () => {
  // Mock comparison logic
  comparisonResult.value = [
    {
      parameter: "Temperature Zone 1",
      golden: "150°C",
      actual: "142°C",
      deviation: 5.3,
    },
    {
      parameter: "Pressure",
      golden: "5.0 bar",
      actual: "4.8 bar",
      deviation: 4.0,
    },
    { parameter: "Cycle Time", golden: "45s", actual: "52s", deviation: 15.5 },
  ];
};
</script>

<style scoped>
.root-cause-page {
  padding: 20px;
}
.comparison-result {
  margin-top: 20px;
}
</style>
