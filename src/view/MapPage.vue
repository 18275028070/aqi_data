<template>
<!-- 
     针对于 /mappage路径显示，在这个组件中，通过子组件注册的方式，要显示出Map.vue这个组件   
 -->
    <div class="com-page">
        <Map></Map>
    </div>
</template>

<script>
    import Map from '../components/Map'
    export default {
        name:'MapPage',
        components:{Map},
    }
</script>

<style>

</style>