<template>
    <!-- 
        针对于 /sellerpage 这条路径而显示出来的
        在这个组件中，通过子组件注册的方式，要显示出seller.vue这个组件
     -->
    <div class="com-page">
        <TemHot />
    </div>
</template>

<script>
    import TemHot from '../components/TemHot'
    export default {
        name:"TemHotPage",
        components:{TemHot}
    }
</script>

<style lang="less" scoped>

</style>