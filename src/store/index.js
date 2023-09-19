import Vue  from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state:{
        theme:'rdf_dark'
    },
    mutations:{
        changeTheme(state){
            if(state.theme==='rdf_dark'){
                state.theme = 'vintage'
            } else {
                state.theme = 'rdf_dark'
            }
        }
    },
    actions:{

    },
    modules:{

    }
})