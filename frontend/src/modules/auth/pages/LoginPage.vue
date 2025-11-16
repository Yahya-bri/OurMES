<template>
  <div class="login">
    <el-card class="login-card">
      <h2>Sign in</h2>
      <el-form @submit.prevent>
        <el-form-item label="Username">
          <el-input v-model="username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="password" type="password" autocomplete="current-password" />
        </el-form-item>
        <el-alert v-if="error" :title="error" type="error" show-icon style="margin-bottom: 12px;" />
        <el-button type="primary" :loading="loading" @click="onLogin">Login</el-button>
      </el-form>
      <p class="hint">Demo users: operator/planner/supervisor/admin (password = username)</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/modules/auth/stores/authStore';
import { ElMessage } from 'element-plus';

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const username = ref('');
const password = ref('');
const error = ref(null);
const loading = ref(false);

const onLogin = async () => {
  loading.value = true;
  error.value = null;
  const ok = await auth.login(username.value, password.value);
  loading.value = false;
  if (ok) {
    ElMessage.success('Welcome!');
    const next = route.query.next || '/';
    router.replace(next);
  } else {
    error.value = auth.error || 'Login failed';
  }
};
</script>

<style scoped>
.login {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
}
.login-card {
  width: 360px;
}
.hint { color: #888; margin-top: 12px; font-size: 12px; }
</style>
